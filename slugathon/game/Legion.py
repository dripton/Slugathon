__copyright__ = "Copyright (c) 2004-2012 David Ripton"
__license__ = "GNU GPL v2"


import types
import logging

from slugathon.util.bag import bag
from slugathon.data import recruitdata, markerdata, playercolordata
from slugathon.game import Creature, Action
from slugathon.util.Observed import Observed


def find_picname(markerid):
    color_name = playercolordata.abbrev_to_name[markerid[:2]]
    index = int(markerid[2:]) - 1
    return markerdata.data[color_name][index]


class Legion(Observed):
    def __init__(self, player, markerid, creatures, hexlabel):
        Observed.__init__(self)
        assert type(hexlabel) == types.IntType
        self.markerid = markerid
        self.picname = find_picname(markerid)
        self.creatures = creatures
        for creature in self.creatures:
            creature.legion = self
        self.hexlabel = hexlabel  # an int not a str
        self.player = player
        self.moved = False
        self.teleported = False
        self.teleporting_lord = None
        self.entry_side = None
        self.previous_hexlabel = None
        self.recruited = False
        # List of tuples of recruiter names
        self.recruiter_names_list = []
        self._angels_pending = 0
        self._archangels_pending = 0

    @property
    def dead(self):
        """Return True iff this legion has been eliminated from battle."""
        if not self.player.has_titan:
            return True
        alive = False
        for creature in self.creatures:
            if creature.dead:
                if creature.is_titan:
                    return True
            else:
                alive = True
        return not alive

    @property
    def living_creatures(self):
        return [creature for creature in self.creatures if not creature.dead]

    @property
    def living_creature_names(self):
        return [creature.name for creature in self.living_creatures]

    @property
    def dead_creatures(self):
        return [creature for creature in self.creatures if creature.dead]

    @property
    def dead_creature_names(self):
        return [creature.name for creature in self.dead_creatures]

    @property
    def any_summonable(self):
        for creature in self.creatures:
            if creature.summonable:
                return True
        return False

    @property
    def any_unknown(self):
        for creature in self.creatures:
            if creature.is_unknown:
                return True
        return False

    @property
    def all_unknown(self):
        for creature in self.creatures:
            if not creature.is_unknown:
                return False
        return True

    @property
    def all_known(self):
        for creature in self.creatures:
            if creature.is_unknown:
                return False
        return True

    @property
    def can_summon(self):
        """Return True if this legion's player has not already summoned this
        turn and any of this player's other unengaged legions has a summonable.
        """
        if len(self) >= 7 or self.player.summoned or self.dead:
            return False
        for legion in self.player.legions:
            if legion != self and not legion.engaged and legion.any_summonable:
                return True
        return False

    @property
    def engaged(self):
        """Return True iff this legion is engaged with an enemy legion."""
        return self.hexlabel in self.player.game.engagement_hexlabels

    def __repr__(self):
        return "Legion %s (%s) in %s %s" % (self.markerid, self.picname,
          self.hexlabel, self.creatures)

    def __len__(self):
        """Return the number of living creatures in the legion."""
        return len(self.living_creature_names)

    def __nonzero__(self):
        """Zero height legions should not be False."""
        return True

    def __eq__(self, other):
        return hasattr(other, "markerid") and self.markerid == other.markerid

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def num_lords(self):
        return sum(creature.is_lord for creature in self.creatures)

    @property
    def first_lord_name(self):
        for creature in self.creatures:
            if creature.is_lord:
                return creature.name
        return None

    @property
    def has_titan(self):
        for creature in self.creatures:
            if creature.is_titan:
                return True
        return False

    @property
    def lord_types(self):
        """Return a set of names of all lords in this legion."""
        types = set()
        for creature in self.creatures:
            if creature.is_lord:
                types.add(creature.name)
        return types

    @property
    def creature_names(self):
        return sorted(creature.name for creature in self.creatures)

    @property
    def mobile_creatures(self):
        return [creature for creature in self.creatures if creature.mobile]

    @property
    def strikers(self):
        return [creature for creature in self.creatures if creature.can_strike]

    @property
    def forced_strikes(self):
        for creature in self.creatures:
            if not creature.struck and creature.engaged_enemies:
                return True
        return False

    def add_creature_by_name(self, creature_name):
        if len(self) >= 7:
            raise ValueError("no room to add another creature")
        creature = Creature.Creature(creature_name)
        creature.legion = self
        self.creatures.append(creature)

    def remove_creature_by_name(self, creature_name):
        for creature in self.creatures:
            if creature.name == creature_name:
                self.creatures.remove(creature)
                return
        raise ValueError("tried to remove missing creature")

    def can_be_split(self, turn):
        if turn == 1:
            return len(self) == 8
        else:
            return len(self) >= 4

    def is_legal_split(self, child1, child2):
        """Return whether this legion can be split into legions child1 and
        child2"""
        logging.info("%s %s", child1, child2)
        if len(self) < 4:
            return False
        if len(self) != len(child1) + len(child2):
            return False
        if len(child1) < 2 or len(child2) < 2:
            return False
        if bag(self.creature_names) != bag(child1.creature_names +
          child2.creature_names) and bag(child1.creature_names).union(bag(
          child2.creature_names)) != bag({"Unknown": len(self)}):
            return False
        if len(self) == 8:
            if len(child1) != 4 or len(child2) != 4:
                return False
            if ((child1.num_lords != 1 or child2.num_lords != 1) and
              ((bag(child1.creature_names) != bag({"Unknown": 4}) or
              bag(child2.creature_names) != bag({"Unknown": 4})))):
                return False
        return True

    def reveal_creatures(self, creature_names):
        """Reveal the creatures from creature_names, if they're not
        already known to be in this legion."""
        if self.any_unknown:
            bag1 = bag(self.creature_names)
            bag2 = bag(creature_names)
            for creature_name, count2 in bag2.iteritems():
                count1 = bag1[creature_name]
                while count2 > count1 and self.any_unknown:
                    self.creatures.remove(Creature.Creature("Unknown"))
                    creature = Creature.Creature(creature_name)
                    self.creatures.append(creature)
                    creature.legion = self
                    count2 -= 1

    def forget_creatures(self):
        """Make all creatures Unknown."""
        self.creatures = Creature.n2c(len(self) * ["Unknown"])
        for creature in self.creatures:
            creature.legion = self

    def move(self, hexlabel, teleport, teleporting_lord, entry_side):
        """Move this legion on the masterboard"""
        self.moved = True
        self.previous_hexlabel = self.hexlabel
        self.hexlabel = hexlabel
        self.teleported = teleport
        self.teleporting_lord = teleporting_lord
        self.entry_side = entry_side
        if teleporting_lord:
            self.reveal_creatures([teleporting_lord])

    def undo_move(self):
        """Undo this legion's last masterboard move"""
        if self.moved:
            self.moved = False
            # XXX This is bogus, but makes repainting the UI easier.
            (self.hexlabel, self.previous_hexlabel) = (self.previous_hexlabel,
              self.hexlabel)
            if self.teleported:
                self.teleported = False
                self.teleporting_lord = None
            self.entry_side = None

    @property
    def can_flee(self):
        return self.num_lords == 0

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
        counts = bag(self.creature_names)
        maximum = 0
        for name, num in counts.iteritems():
            if (num > maximum and Creature.Creature(name).is_creature):
                maximum = num
        return maximum

    @property
    def can_recruit(self):
        """Return True iff the legion can currently recruit, if it moved
        or defended in a battle.
        """
        logging.info("can_recruit %s len %s recruited %s dead %s",
          self, len(self), self.recruited, self.dead)
        if len(self) >= 7 or self.recruited or self.dead:
            return False
        game = self.player.game
        mterrain = game.board.hexes[self.hexlabel].terrain
        caretaker = game.caretaker
        return bool(self.available_recruits_and_recruiters(mterrain,
          caretaker))

    def could_recruit(self, mterrain, caretaker):
        """Return True iff the legion could recruit in a masterhex with
        terrain type mterrain, if it moved there and was the right height
        and had not already recruited this turn."""
        return bool(self.available_recruits_and_recruiters(mterrain,
          caretaker))

    def available_recruits(self, mterrain, caretaker):
        """Return a list of the creature names that this legion could
        recruit in a masterhex with terrain type mterrain, if it moved there.

        The list is sorted in the same order as within recruitdata.
        """
        recruits = []
        for tup in self.available_recruits_and_recruiters(mterrain,
          caretaker):
            recruit = tup[0]
            if recruit not in recruits:
                recruits.append(recruit)
        return recruits

    def available_recruits_and_recruiters(self, mterrain, caretaker):
        """Return a list of tuples with creature names and recruiters that this
        legion could recruit in a masterhex with terrain type mterrain, if it
        moved there.

        Each tuple will contain the recruit as its first element, and the
        recruiters (if any) as its remaining elements.

        The list is sorted in the same order as within recruitdata.
        """
        result_list = []
        counts = bag(self.living_creature_names)
        recruits = recruitdata.data[mterrain]
        for sublist in self._gen_sublists(recruits):
            names = [tup[0] for tup in sublist]
            nums = [tup[1] for tup in sublist]
            for ii in xrange(len(sublist)):
                name = names[ii]
                num = nums[ii]
                if ii >= 1:
                    prev = names[ii - 1]
                else:
                    prev = None
                if prev == recruitdata.ANYTHING:
                    # basic tower creature
                    for jj in xrange(ii + 1):
                        if nums[jj] and caretaker.counts.get(names[jj]):
                            result_list.append((names[jj],))
                else:
                    if (prev == recruitdata.CREATURE and
                      self._max_creatures_of_one_type() >= num):
                        # guardian
                        recruiters = []
                        for name2, num2 in counts.iteritems():
                            if (num2 >= num and Creature.Creature(
                              name2).is_creature):
                                recruiters.append(name2)
                        for jj in xrange(ii + 1):
                            if nums[jj] and caretaker.counts.get(names[jj]):
                                for recruiter in recruiters:
                                    li = [names[jj]]
                                    for kk in xrange(num):
                                        li.append(recruiter)
                                    tup = tuple(li)
                                    result_list.append(tup)
                    if counts[prev] >= num:
                        # recruit up
                        if num and caretaker.counts.get(name):
                            li = [name]
                            for kk in xrange(num):
                                li.append(prev)
                            tup = tuple(li)
                            result_list.append(tup)
                    if counts[name] and num:
                        # recruit same or down
                        for jj in xrange(ii + 1):
                            if nums[jj] and caretaker.counts.get(names[jj]):
                                result_list.append((names[jj], name))

        def cmp_helper(tup1, tup2):
            ii = 0
            while True:
                if len(tup1) < ii + 1:
                    return -1
                if len(tup2) < ii + 1:
                    return 1
                if tup1[ii] != tup2[ii]:
                    c1 = Creature.Creature(tup1[ii])
                    c2 = Creature.Creature(tup2[ii])
                    diff = 100 * (c1.sort_value - c2.sort_value)
                    if diff != 0:
                        return int(diff)
                ii += 1

        result_list.sort(cmp=cmp_helper)
        return result_list

    def recruit_creature(self, creature, recruiter_names):
        """Recruit creature."""
        logging.info("Legion.recruit_creature %s %s %s", self, creature,
          recruiter_names)
        if self.recruited:
            logging.info("already recruited")
            if self.creatures[-1].name == creature.name:
                # okay, don't do it twice
                pass
            else:
                raise AssertionError("legion tried to recruit twice")
        else:
            if len(self) >= 7:
                logging.info(self)
                raise AssertionError("legion too tall to recruit")
            caretaker = self.player.game.caretaker
            if not caretaker.num_left(creature.name):
                raise AssertionError("none of creature left")
            caretaker.take_one(creature.name)
            self.creatures.append(creature)
            self.recruiter_names_list.append(recruiter_names)
            creature.legion = self
            self.reveal_creatures([creature.name] + list(recruiter_names))
            self.recruited = True

    def undo_recruit(self):
        """Undo last recruit, and notify observers."""
        # Avoid double undo
        if not self.recruited:
            return
        player = self.player
        creature = self.creatures.pop()
        recruiter_names = self.recruiter_names_list.pop()
        logging.info("%s clearing self.recruited", self)
        self.recruited = False
        caretaker = self.player.game.caretaker
        caretaker.put_one_back(creature.name)
        action = Action.UndoRecruit(player.game.name, player.name,
          self.markerid, creature.name, recruiter_names)
        self.notify(action)

    def unreinforce(self):
        """Undo reinforcement, and notify observers."""
        # Avoid double undo
        if not self.recruited:
            return
        player = self.player
        creature = self.creatures.pop()
        recruiter_names = self.recruiter_names_list.pop()
        logging.info("%s clearing self.recruited", self)
        self.recruited = False
        caretaker = self.player.game.caretaker
        caretaker.put_one_back(creature.name)
        action = Action.UnReinforce(player.game.name, player.name,
          self.markerid, creature.name, recruiter_names)
        self.notify(action)

    @property
    def score(self):
        """Return the point value of this legion."""
        return sum(creature.score for creature in self.creatures)

    @property
    def living_creatures_score(self):
        """Return the point value of living creatures in this legion.

        Used to award half points when a player's titan dies, but some
        of the creatures in its legion remain alive.
        """
        return sum(creature.score for creature in self.living_creatures)

    @property
    def sorted_creatures(self):
        """Return creatures, sorted in descending order of value."""
        li = reversed(sorted((creature.sort_value, creature)
          for creature in self.creatures))
        return [tup[1] for tup in li]

    @property
    def sorted_living_creatures(self):
        """Return living creatures, sorted in descending order of value."""
        li = reversed(sorted((creature.sort_value, creature)
          for creature in self.creatures if not creature.dead))
        return [tup[1] for tup in li]

    @property
    def sort_value(self):
        """Return a rough indication of legion value."""
        return sum(creature.sort_value for creature in self.living_creatures)

    @property
    def combat_value(self):
        """Return a rough indication of legion combat value."""
        return sum(creature.combat_value for creature in self.living_creatures)

    def native_fraction(self, hazard):
        """Return the fraction of this legion that's native to hazard."""
        native = 0
        not_native = 0
        for creature in self.creatures:
            if creature.is_native(hazard):
                native += 1
            else:
                not_native += 1
        total = native + not_native
        if total == 0:
            return 0
        else:
            return 1.0 * native / total

    @property
    def terrain_combat_value(self):
        """Return a rough indication of legion combat value, considering its
        current terrain."""
        TOWER_BONUS = 0.25
        BRUSH_BONUS = 0.1
        JUNGLE_BONUS = 0.1
        HILLS_BONUS = 0.1
        SWAMP_BONUS = 0.05
        MARSH_BONUS = 0.05
        DESERT_BONUS = 0.1
        MOUNTAINS_BONUS = 0.1
        TUNDRA_BONUS = 0.1
        base_value = self.combat_value
        terrain = self.player.game.board.hexes[self.hexlabel].terrain
        if terrain == "Tower":
            return (1 + TOWER_BONUS) * base_value
        elif terrain == "Brush":
            return ((1 + (self.native_fraction("Bramble") * BRUSH_BONUS)) *
              base_value)
        elif terrain == "Jungle":
            return ((1 + (self.native_fraction("Bramble") * JUNGLE_BONUS)) *
              base_value)
        elif terrain == "Hills":
            return ((1 + (self.native_fraction("Slope") * HILLS_BONUS)) *
              base_value)
        elif terrain == "Swamp":
            return ((1 + (self.native_fraction("Bog") * SWAMP_BONUS)) *
              base_value)
        elif terrain == "Marsh":
            return ((1 + (self.native_fraction("Bog") * MARSH_BONUS)) *
              base_value)
        elif terrain == "Desert":
            return ((1 + (self.native_fraction("Dune") * DESERT_BONUS)) *
              base_value)
        elif terrain == "Mountain":
            return ((1 + (self.native_fraction("Slope") * MOUNTAINS_BONUS)) *
              base_value)
        elif terrain == "Tundra":
            return ((1 + (self.native_fraction("Drift") * TUNDRA_BONUS)) *
              base_value)
        else:
            return base_value

    def die(self, scoring_legion, fled, no_points, check_for_victory=True,
      kill_all_creatures=False):
        logging.info("Legion.die %s %s %s %s %s", self, scoring_legion, fled,
          no_points, check_for_victory)
        if scoring_legion is not None and not no_points:
            # We only give points for dead creatures, not living creatures,
            # to handle the case where a titan dies but leaves survivors,
            # who will give half-points later.
            if kill_all_creatures:
                points = self.score
            else:
                points = sum(creature.score for creature in self.creatures if
                  creature.dead)
            if fled:
                points //= 2
            scoring_legion.add_points(points, True)
        caretaker = self.player.game.caretaker
        dead_titan = False
        for creature in self.creatures:
            caretaker.kill_one(creature.name)
            if creature.is_titan:
                logging.info("setting dead_titan")
                dead_titan = True
        if dead_titan:
            self.player.die(scoring_legion.player, check_for_victory)
        # We do this last, so that any living allies of a dead titan remain
        # long enough to give half points.
        self.player.remove_legion(self.markerid)

    def add_points(self, points, can_acquire_angels):
        logging.info("Legion.add_points %s %s %s", self, points,
          can_acquire_angels)
        ARCHANGEL_POINTS = Creature.Creature("Archangel").acquirable_every
        ANGEL_POINTS = Creature.Creature("Angel").acquirable_every
        player = self.player
        score0 = player.score
        score1 = score0 + points
        player.score = score1
        logging.info("%s now has score %s", player, player.score)
        if can_acquire_angels:
            height = len(self)
            archangels = 0
            if (height < 7 and
              score1 // ARCHANGEL_POINTS > score0 // ARCHANGEL_POINTS):
                archangels += 1
                score1 -= ANGEL_POINTS
            logging.info("archangels %d" % archangels)
            angels = 0
            while (height + archangels + angels < 7 and
              score1 // ANGEL_POINTS > score0 // ANGEL_POINTS):
                angels += 1
                score1 -= ANGEL_POINTS
            logging.info("angels %d" % angels)
            self._angels_pending = angels
            self._archangels_pending = archangels
            if angels + archangels > 0:
                action = Action.CanAcquireAngels(self.player.game.name,
                  self.player.name, self.markerid, angels, archangels)
                self.notify(action)

    @property
    def angels_pending(self):
        if len(self) >= 7:
            self._angels_pending = 0
            self._archangels_pending = 0
        return self._angels_pending

    @property
    def archangels_pending(self):
        if len(self) >= 7:
            self._angels_pending = 0
            self._archangels_pending = 0
        return self._archangels_pending

    def acquire_angels(self, angels):
        """Acquire angels."""
        logging.info("acquire_angels %s", angels)
        num_archangels = num_angels = 0
        for angel in angels:
            if angel.name == "Archangel":
                num_archangels += 1
            elif angel.name == "Angel":
                num_angels += 1
        caretaker = self.player.game.caretaker
        if self.player.game.master:
            okay = (num_archangels <= self.archangels_pending and
              num_angels <= self.angels_pending + self.archangels_pending -
              num_archangels)
            if not okay:
                logging.info("not enough angels pending")
                logging.info("angels %s", angels)
                logging.info("angels_pending %s", self.angels_pending)
                logging.info("archangels_pending %s", self.archangels_pending)
                return
            if len(self) >= 7:
                logging.info("acquire_angels 7 high")
                self._angels_pending = 0
                self._archangels_pending = 0
                return
            if len(self) + num_angels + num_archangels > 7:
                logging.info("acquire_angels would go over 7 high")
                return
            while caretaker.num_left("Archangel") < num_archangels:
                logging.info("not enough Archangels left")
                return
            while caretaker.num_left("Angel") < num_angels:
                return
        self._archangels_pending -= num_archangels
        if self.archangels_pending < 0:
            self._archangels_pending = 0
        self._angels_pending -= num_angels
        if self.angels_pending < 0:
            self._angels_pending = 0
        for angel in angels:
            caretaker.take_one(angel.name)
            self.creatures.append(angel)
            angel.legion = self
        self._angels_pending = 0
        self._archangels_pending = 0
        logging.info("end of acquire_angels %s", self)

    def do_not_acquire_angels(self):
        """Do not acquire any angels, and notify observers."""
        logging.info("do_not_acquire_angels %s", self)
        if self.angels_pending or self.archangels_pending:
            self.reset_angels_pending()
            action = Action.DoNotAcquireAngels(self.player.game.name,
              self.player.name, self.markerid)
            self.notify(action)

    def reset_angels_pending(self):
        if self.angels_pending or self.archangels_pending:
            logging.info("reset_angels_pending")
            self._angels_pending = 0
            self._archangels_pending = 0

    def enter_battle(self, hexlabel):
        for creature in self.creatures:
            creature.hexlabel = hexlabel

    def find_creature(self, creature_name, hexlabel):
        """Return the Creature with creature_name at hexlabel, or None."""
        for creature in self.creatures:
            if (creature.name == creature_name and creature.hexlabel ==
              hexlabel):
                return creature
        return None
