import types

from bag import bag
import recruitdata
import Creature
from Observed import Observed
import Action

class Legion(Observed):
    def __init__(self, player, markername, creatures, hexlabel):
        Observed.__init__(self)
        assert type(hexlabel) == types.IntType
        self.markername = markername
        self.creatures = creatures
        for creature in self.creatures:
            creature.legion = self
        # TODO Should we store the actual MasterHex instead?
        self.hexlabel = hexlabel  # an int not a str
        self.player = player
        self.moved = False
        self.teleported = False
        self.teleporting_lord = None
        self.entry_side = None
        self.previous_hexlabel = None
        self.recruited = False
        self.angels_pending = 0
        self.archangels_pending = 0

    def __repr__(self):
        return "Legion %s in %s %s" % (self.markername, self.hexlabel,
          self.creatures)

    def __len__(self):
        return len(self.creatures)

    def num_lords(self):
        return sum(creature.character_type == "lord" for creature in
          self.creatures)

    def first_lord_name(self):
        for creature in self.creatures:
            if creature.character_type == "lord":
                return creature.name
        return None

    def creature_names(self):
        return sorted(creature.name for creature in self.creatures)

    def add_creature_by_name(self, creature_name):
        if len(self) >= 7:
            raise ValueError, "no room to add another creature"
        creature = Creature.Creature(creature_name)
        creature.legion = self
        self.creatures.append(creature)

    def remove_creature_by_name(self, creature_name):
        for creature in self.creatures:
            if creature.name == creature_name:
                self.creatures.remove(creature)
                return
        raise ValueError, "tried to remove missing creature"

    def can_be_split(self, turn):
        if turn == 1:
            return len(self) == 8
        else:
            return len(self) >= 4

    def is_legal_split(self, child1, child2):
        """Return whether this legion can be split into legions child1 and
        child2"""
        if len(self) < 4:
            return False
        if len(self) != len(child1) + len(child2):
            return False
        if len(child1) < 2 or len(child2) < 2:
            return False
        if not bag(self.creature_names()) == bag(child1.creature_names() +
          child2.creature_names()):
            return False
        if len(self) == 8:
            if len(child1) != 4 or len(child2) != 4:
                return False
            if child1.num_lords() != 1 or child2.num_lords() != 1:
                return False
        return True

    def move(self, hexlabel, teleport, teleporting_lord, entry_side):
        """Move this legion on the masterboard"""
        self.moved = True
        self.previous_hexlabel = self.hexlabel
        self.hexlabel = hexlabel
        self.teleported = teleport
        self.teleporting_lord = teleporting_lord
        self.entry_side = entry_side

    def undo_move(self):
        """Undo this legion's last masterboard move"""
        if self.moved:
            self.moved = False
            # XXX This is bogus, but makes repainting the UI easier.
            (self.hexlabel, self.previous_hexlabel) = (self.previous_hexlabel,
              self.hexlabel)
            if self.teleported:
                self.teleported = False
                self.player.teleported = False
                self.teleporting_lord = None
            self.entry_side = None

    def can_flee(self):
        return self.num_lords() == 0

    def _gen_sublists(self, recruits):
        """Generate a sublist of recruits, within which up- and down-recruiting
        is possible."""
        sublist = []
        for tup in recruits:
            if tup:
                sublist.append(tup)
            else:
                yield sublist
                sublist = []
        yield sublist

    def _max_creatures_of_one_type(self):
        """Return the maximum number of creatures (not lords or demi-lords) of
        the same type in this legion."""
        counts = bag(self.creature_names())
        maximum = 0
        for name, num in counts.iteritems():
            if (num > maximum and Creature.Creature(name).character_type ==
              "creature"):
                maximum = num
        return maximum

    def available_recruits(self, masterhex, caretaker):
        """Return a list of the creature names that this legion could
        recruit in masterhex, if it moved there.

        The list is sorted in the same order as within recruitdata.
        """
        result_set = set()
        counts = bag(self.creature_names())
        recruits = recruitdata.data[masterhex.terrain]
        for sublist in self._gen_sublists(recruits):
            names = [tup[0] for tup in sublist]
            nums = [tup[1] for tup in sublist]
            ii = len(sublist) - 1
            while ii >= 0:
                name = names[ii]
                num = nums[ii]
                if ii >= 1:
                    prev = names[ii - 1]
                else:
                    prev = None
                if ((counts[name] and num) or (counts[prev] >= num) or
                  prev == recruitdata.ANYTHING or (prev == recruitdata.CREATURE
                  and self._max_creatures_of_one_type() >= num)):
                    for jj in xrange(0, ii+1):
                        if nums[jj]:
                            result_set.add(names[jj])
                    break
                ii -= 1
        # Order matters, so revisit the original recruits list.  Also check
        # the caretaker.
        result_list = []
        for tup in recruits:
            if tup:
                name = tup[0]
                if name in result_set and caretaker.counts.get(name):
                    result_list.append(name)
        return result_list

    def recruit(self, creature):
        """Recruit creature, and notify observers."""
        player = self.player
        if self.recruited:
            if self.creatures[-1].name == creature.name:
                # okay, don't do it twice
                pass
            else:
                raise AssertionError("legion tried to recruit twice")
        else:
            if len(self) >= 7:
                raise AssertionError("legion too tall to recruit")
            caretaker = self.player.game.caretaker
            if not caretaker.num_left(creature.name):
                raise AssertionError("none of creature left")
            caretaker.take_one(creature.name)
            self.creatures.append(creature)
            creature.legion = self
            self.recruited = True
            action = Action.RecruitCreature(player.game.name, player.name,
              self.markername, creature.name)
            self.notify(action)

    def undo_recruit(self):
        """Undo last recruit, and notify observers."""
        # Avoid double undo
        if not self.recruited:
            return
        player = self.player
        creature = self.creatures.pop()
        self.recruited = False
        caretaker = self.player.game.caretaker
        caretaker.put_one_back(creature.name)
        action = Action.UndoRecruit(player.game.name, player.name,
          self.markername, creature.name)
        self.notify(action)

    def score(self):
        """Return the point value of this legion."""
        total = 0
        for creature in self.creatures:
            total += creature.score()
        return total

    def sorted_creatures(self):
        """Return creatures, sorted in descending order of value."""
        li = reversed(sorted((creature.sort_value(), creature)
          for creature in self.creatures))
        return [tup[1] for tup in li]

    def die(self, scoring_legion, fled):
        if scoring_legion is not None:
            points = self.score()
            if fled:
                points //= 2
            scoring_legion.add_points(points, True)
        caretaker = self.player.game.caretaker
        dead_titan = False
        for creature in self.creatures:
            caretaker.kill_one(creature.name)
            if creature.name == "Titan":
                dead_titan = True
        self.player.remove_legion(self.markername)
        if dead_titan:
            self.player.die(scoring_legion)

    def add_points(self, points, can_acquire):
        # TODO Move these to a data file
        ARCHANGEL_POINTS = 500
        ANGEL_POINTS = 100
        player = self.player
        score0 = player.score
        score1 = score0 + points
        player.score = score1
        if can_acquire:
            archangels = 0
            while (len(self) + archangels < 7 and
              score1 // ARCHANGEL_POINTS > score0 // ARCHANGEL_POINTS):
                archangels += 1
                score1 -= ANGEL_POINTS
            angels = 0
            while (len(self) + archangels + angels < 7 and
              score1 // ANGEL_POINTS > score0 // ANGEL_POINTS):
                angels += 1
                score1 -= ANGEL_POINTS
            self.angels_pending = angels
            self.archangels_pending = archangels
            if angels + archangels > 0:
                action = Action.AcquireAngels(self.player.game.name,
                  self.player.name, self.markername, angels, archangels)
                self.notify(action)


    def acquire(self, angel):
        """Acquire angel, and notify observers."""
        if angel.name == "Archangel":
            okay = self.archangels_pending > 0
        elif angel.name == "Angel":
            okay = self.archangels_pending > 0 or self.angels_pending > 0
        if not okay:
            return
        if len(self) >= 7:
            raise AssertionError("legion too tall to recruit")
        caretaker = self.player.game.caretaker
        if not caretaker.num_left(angel.name):
            raise AssertionError("none of angel left")
        caretaker.take_one(angel.name)
        self.creatures.append(angel)
        angel.legion = self
        if angel.name == "Archangel" or self.angels_pending < 1:
            self.archangels_pending -= 1
        else:
            self.angels_pending -= 1
        action = Action.AcquireAngel(self.player.game.name, self.player.name,
          self.markername, angel.name)
        self.notify(action)

    def reset_angels_pending(self):
        self.angels_pending = 0
        self.archangels_pending = 0

    def enter_battle(self, hexlabel):
        for creature in self.creatures:
            creature.hexlabel = hexlabel
