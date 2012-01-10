__copyright__ = "Copyright (c) 2003-2012 David Ripton"
__license__ = "GNU GPL v2"


"""Split prediction for the AI."""


import copy
import itertools

from slugathon.game.Creature import Creature


def superset(big, little):
    """Return True if list big is a superset of list little."""
    for el in little:
        if big.count(el) < little.count(el):
            return False
    return True


def subtract_lists(big, little):
    """Return the elements of big, minus the elements of little.

    If big is not a superset of little, raise an exception.
    """
    assert superset(big, little)
    li = big[:]
    for el in little:
        li.remove(el)
    return li


def num_creature(li, creature_name):
    """Return the number of elements of the list with .name creature_name."""
    count = 0
    for ci in li:
        if ci.name == creature_name:
            count += 1
    return count


def get_creature_info(li, creature_name):
    """Return the first CreatureInfo that matches the passed name.

    Return None if no matching CreatureInfo is found.
    """
    for ci in li:
        if ci.name == creature_name:
            return ci
    return None


def get_creature_names(li):
    """Return .name for each element in the list."""
    return [ci.name for ci in li]


def remove_last_uncertain_creature(li):
    """Remove the last uncertain creature from the list.

    Raise if there are no uncertain creatures.
    """
    try:
        li.reverse()
        for ii, ci in enumerate(li):
            if not ci.certain:
                del li[ii]    # li.remove(ci) can remove the wrong one
                return
    finally:
        li.reverse()
    raise ValueError("No uncertain creatures")


def min_count(lili, name):
    """Return the minimum number of times name appears in any of the lists
    contained in the list of lists."""
    return min([li.count(name) for li in lili])


def max_count(lili, name):
    """Return the maximum number of times name appears in any of the lists
    contained in the list of lists."""
    return max([li.count(name) for li in lili])


class CreatureInfo(Creature):
    """A Creature with some extra attributes for split prediction."""
    def __init__(self, name, certain, at_split):
        Creature.__init__(self, name)
        self.certain = certain
        self.at_split = at_split

    def __repr__(self):
        st = self.name
        if not self.certain:
            st += "?"
        if not self.at_split:
            st += "*"
        return st

    def __hash__(self):
        """Two CreatureInfo objects match if the names match."""
        return self.name

    def sort_key(self):
        """Sort by sort_value descending, then by name."""
        return (-self.sort_value, self.name)


class Node(object):
    """A view of a Legion at a point in time."""
    def __init__(self, markerid, turn_created, creatures, parent):
        self.markerid = markerid     # Not unique!
        self.turn_created = turn_created
        self.creatures = creatures   # list of CreatureInfo
        self.removed = []            # list of CreatureInfo, only if at_split
        self.parent = parent
        self.clear_children()

    def clear_children(self):
        """Clear out all child nodes."""
        # All are at the time this node was split.
        self.child_size2 = 0   # size of the smaller splitoff
        self.child1 = None     # child1 is the presumed "better" legion
        self.child2 = None
        self.turn_split = -1

    @property
    def _full_name(self):
        """markerid and turn_created"""
        return self.markerid + "(" + str(self.turn_created) + ")"

    def __repr__(self):
        """Show a string with both current and removed creatures."""
        self.creatures.sort(key=CreatureInfo.sort_key)
        st = self._full_name + ":"
        for ci in self.creatures:
            st += " " + str(ci)
        for ci in self.removed:
            st += " " + str(ci) + "-"
        return st

    def sort_key(self):
        """Sort by turn_created then by markerid."""
        return (self.turn_created, self.markerid)

    @property
    def certain_creatures(self):
        """Return list of CreatureInfo where certain is true."""
        return [ci for ci in self.creatures if ci.certain]

    @property
    def num_certain_creatures(self):
        """Return number of certain creatures."""
        return len(self.certain_creatures)

    @property
    def num_uncertain_creatures(self):
        """Return number of uncertain creatures."""
        return len(self) - self.num_certain_creatures

    @property
    def all_certain(self):
        """Return True if all creatures are certain."""
        for ci in self.creatures:
            if not ci.certain:
                return False
        return True

    @property
    def has_split(self):
        """Return True if this legion has split."""
        if self.child1 is None and self.child2 is None:
            return False
        # A legion can have no children, or two, but not one.
        assert self.child1 is not None and self.child2 is not None
        return True

    @property
    def children(self):
        """Return a list of this node's child nodes."""
        if self.has_split:
            return [self.child1, self.child2]
        else:
            return []

    @property
    def all_descendents_certain(self):
        """Return True if all of this node's children, grandchildren, etc.
        have no uncertain creatures."""
        for child in self.children:
            if not child.all_certain or not child.all_descendents_certain:
                return False
        return True

    @property
    def after_split_creatures(self):
        """Return list of CreatureInfo where at_split is false."""
        return [ci for ci in self.creatures if not ci.at_split]

    @property
    def certain_at_split_or_removed_creatures(self):
        """Return list of CreatureInfo where both certain and at_split are
        true, plus removed creatures."""
        alive = [ci for ci in self.creatures if ci.certain and ci.at_split]
        dead = self.removed[:]
        return alive + dead

    @property
    def other_child_markerid(self):
        """Return the child markerid that's different from this node's
        markerid, or None."""
        for child in self.children:
            if child.markerid != self.markerid:
                return child.markerid
        return None

    def __len__(self):
        return len(self.creatures)

    @property
    def creature_names(self):
        """Return this node's creatures' names, in sorted order."""
        return sorted((creature.name for creature in self.creatures))

    def reveal_creatures(self, cnl):
        """Reveal all creatures in the creature name list as certain.

        Return True iff new information was sent to this legion's parent.
        """
        if ((not cnl) or
          (superset(get_creature_names(self.certain_creatures), cnl)
          and (self.all_descendents_certain))):
            return False

        cil = [CreatureInfo(name, True, True) for name in cnl]

        # Use a copy rather than the original so we can remove
        # creatures as we check for multiples.
        dupe = copy.deepcopy(cil)

        # Confirm that all creatures that were certain still fit
        # along with the revealed creatures.
        count = len(dupe)
        for ci in self.certain_creatures:
            if ci in dupe:
                dupe.remove(ci)
            else:
                count += 1

        assert len(self) >= count, \
            "Certainty error in reveal_creatures count=%d height=%d" \
              % (count, len(self))

        # Then mark passed creatures as certain and then
        # communicate this to the parent, to adjust other legions.

        dupe = copy.deepcopy(cil)
        count = 0
        for ci in dupe:
            ci.certain = True
            ci.at_split = True   # If not at_split, would be certain.
            if num_creature(self.creatures, ci.name) < num_creature(dupe,
              ci.name):
                self.creatures.append(ci)
                count += 1

        # Ensure that the creatures in cnl are now marked as certain
        dupe = copy.deepcopy(cil)
        for ci in self.certain_creatures:
            if ci in dupe:
                dupe.remove(ci)
        for ci in dupe:
            for ci2 in self.creatures:
                if not ci2.certain and ci2.name == ci.name:
                    ci2.certain = True
                    break

        # Need to remove count uncertain creatures.
        for unused in xrange(count):
            remove_last_uncertain_creature(self.creatures)
        if self.parent is None:
            return False
        else:
            self.parent.update_child_contents()
            return True

    def update_child_contents(self):
        """Tell this parent legion the updated contents of its children."""
        names = []
        for child in self.children:
            names.extend(get_creature_names(
              child.certain_at_split_or_removed_creatures))
        told_parent = self.reveal_creatures(names)
        if not told_parent:
            self.split(self.child_size2, self.other_child_markerid)

    @property
    def is_legal_initial_splitoff(self):
        """Return True if this Node is a valid turn 1 splitoff."""
        if len(self) != 4:
            return False
        names = self.creature_names
        return (names.count("Titan") + names.count("Angel") == 1)

    def _find_all_possible_splits(self, child_size, known_keep, known_split):
        """Return a list of lists of all legal combinations of splitoff names.

        Raise if the combination of known_keep and known_split contains
        uncertain creatures.
        """
        # Sanity checks
        assert child_size >= len(known_split), \
          "More known splitoffs than splitoffs"
        assert len(self) <= 8
        if len(self) == 8:
            assert child_size == 4
            assert "Titan" in get_creature_names(self.creatures)
            assert "Angel" in get_creature_names(self.creatures)

        known_combo = known_split + known_keep
        certain = get_creature_names(self.certain_creatures)
        assert superset(certain, known_combo), \
          "known_combo contains uncertain creatures"

        unknowns = get_creature_names(self.creatures)
        for name in known_combo:
            unknowns.remove(name)

        num_unknowns_to_split = child_size - len(known_split)

        unknown_combos = itertools.combinations(unknowns,
          num_unknowns_to_split)
        possible_splits_set = set()
        for combo in unknown_combos:
            pos = tuple(known_split + list(combo))
            if len(self) != 8:
                possible_splits_set.add(pos)
            else:
                cil = [CreatureInfo(name, False, True) for name in pos]
                pos_node = Node(self.markerid, -1, cil, self)
                if pos_node.is_legal_initial_splitoff:
                    possible_splits_set.add(pos)
        possible_splits = [list(pos) for pos in possible_splits_set]
        return possible_splits

    def _choose_creatures_to_split_out(self, possible_splits):
        """Decide how to split this legion, and return a list of creature
        names to remove.

        Return empty list on error.
        """
        maximize = (2 * len(possible_splits[0]) > len(self))

        best_sort_value = None
        creatures_to_remove = []
        for li in possible_splits:
            total_sort_value = 0
            for name in li:
                creature = Creature(name)
                total_sort_value += creature.sort_value
            if ((best_sort_value is None) or
              (maximize and total_sort_value > best_sort_value) or
              (not maximize and total_sort_value < best_sort_value)):
                best_sort_value = total_sort_value
                creatures_to_remove = li
        return creatures_to_remove

    def _split_children(self):
        """Recursively split this node's children."""
        for child in self.children:
            if child.has_split:
                child.split(child.child_size2, child.other_child_markerid)

    def split(self, child_size, other_markerid, turn=-1):
        """Split this legion."""
        assert len(self) <= 8

        if turn == -1:
            turn = self.turn_split   # Re-predicting earlier split
        else:
            self.turn_split = turn   # New split

        if self.has_split:
            known_keep1 = get_creature_names(
              self.child1.certain_at_split_or_removed_creatures)
            known_split1 = get_creature_names(
              self.child2.certain_at_split_or_removed_creatures)
        else:
            known_keep1 = []
            known_split1 = []
        known_combo = known_keep1 + known_split1
        certain = get_creature_names(self.certain_creatures)
        if not superset(certain, known_combo):
            # We need to abort this split and trust that it will be redone
            # after the certainty information percolates up to the parent.
            return
        all_names = get_creature_names(self.creatures)
        uncertain = subtract_lists(all_names, certain)

        possible_splits = self._find_all_possible_splits(child_size,
          known_keep1, known_split1)
        splitoff_names = self._choose_creatures_to_split_out(possible_splits)

        possible_keeps = [subtract_lists(all_names, names) for names in
          possible_splits]

        def find_certain_child(certain, uncertain, possibles):
            """Return a list of names that are certainly in the child node."""
            li = []
            for name in set(certain):
                min_ = min_count(possibles, name) - uncertain.count(name)
                li.extend(min_ * [name])
            return li

        known_keep2 = find_certain_child(certain, uncertain, possible_keeps)
        known_split2 = find_certain_child(certain, uncertain, possible_splits)

        def merge_knowns(known1, known2):
            """Return a merged list of names from the two lists."""
            all_names = set(known1 + known2)
            li = []
            for name in all_names:
                max_ = max_count([known1, known2], name)
                li.extend(max_ * [name])
            return li

        known_keep = merge_knowns(known_keep1, known_keep2)
        known_split = merge_knowns(known_split1, known_split2)

        def _inherit_parent_certainty(certain, known, other):
            """If one of the child legions is fully known, assign the
            creatures in the other child legion the same certainty they
            have in the parent.
            """
            all_names = certain[:]
            assert superset(all_names, known)
            for name in known:
                all_names.remove(name)
            assert superset(all_names, other)
            for name in all_names:
                if all_names.count(name) > other.count(name):
                    other.append(name)

        if len(known_split) == child_size:
            _inherit_parent_certainty(certain, known_split, known_keep)
        elif len(known_keep) == len(self) - child_size:
            _inherit_parent_certainty(certain, known_keep, known_split)

        # lists of CreatureInfo
        strong_list = []
        weak_list = []
        for ci in self.creatures:
            name = ci.name
            new_info = CreatureInfo(name, False, True)
            if name in splitoff_names:
                weak_list.append(new_info)
                splitoff_names.remove(name)
                # If in known_split, set certain
                if name in known_split:
                    known_split.remove(name)
                    new_info.certain = True
            else:
                strong_list.append(new_info)
                # If in known_keep, set certain
                if name in known_keep:
                    known_keep.remove(name)
                    new_info.certain = True

        if self.has_split:
            strong_list += self.child1.after_split_creatures
            for ci in self.child1.removed:
                strong_list.remove(ci)
            weak_list += self.child2.after_split_creatures
            for ci in self.child2.removed:
                weak_list.remove(ci)
            self.child1.creatures = strong_list
            self.child2.creatures = weak_list
        else:
            self.child1 = Node(self.markerid, turn, strong_list, self)
            self.child2 = Node(other_markerid, turn, weak_list, self)
            self.child_size2 = len(self.child2)

        self._split_children()

    def merge(self, other, turn):
        """Recombine this legion and other, because it was not possible to
        move either one.

        The two legions must share the same parent.  If either legion has the
        parent's markerid, then that legion will remain. Otherwise this legion
        will remain.
        """
        parent = self.parent
        assert parent == other.parent
        if (parent.markerid == self.markerid or
          parent.markerid == other.markerid):
            # Remove self and other from parent, as if the split never
            # happened.  The parent will then be a leaf node.
            parent.clear_children()
        else:
            # Remove self and other, then resplit parent into self.
            parent.clear_children()
            parent.split(len(self) + len(other), self.markerid, turn)

    def add_creature(self, creature_name):
        """Add a Creature by its name."""
        # Allow adding to 7-high legion, to support the case of summoning
        # into a legion that has lost creatures whose removal has not
        # been noted yet.
        ci = CreatureInfo(creature_name, True, False)
        self.creatures.append(ci)

    def remove_creature(self, creature_name):
        """Remove a Creature by its name."""
        if not self:
            raise ValueError("Tried removing from 0-high legion")
        self.reveal_creatures([creature_name])
        ci = get_creature_info(self.certain_creatures, creature_name)
        assert ci is not None

        # Only need to track the removed creature for future parent split
        # predictions if it was here at the time of the split.
        if ci.at_split:
            self.removed.append(ci)
        for (ii, creature) in enumerate(self.creatures):
            if creature == ci and creature.certain:
                del self.creatures[ii]
                break

    def remove_creatures(self, creature_names):
        """Remove Creatures by their names."""
        self.reveal_creatures(creature_names)
        for name in creature_names:
            self.remove_creature(name)


class PredictSplits(object):
    """Split predictor."""
    def __init__(self, playername, root_id, creature_names):
        self.playername = playername
        # All creatures in root legion must be known
        creatures = [CreatureInfo(name, True, True) for name in creature_names]
        self.root = Node(root_id, 0, creatures, None)

    def get_nodes(self, root=None):
        """Return all nodes in subtree starting from root."""
        if root is None:
            root = self.root
        nodes = [root]
        for child in root.children:
            nodes += self.get_nodes(child)
        return nodes

    def get_leaves(self, root=None):
        """Return all non-empty childless nodes in subtree."""
        if root is None:
            root = self.root
        leaves = []
        if not root.has_split:
            if root:
                leaves.append(root)
        else:
            for child in root.children:
                leaves += self.get_leaves(child)

        # If duplicate markerids, prune the older node.
        prune_these = set()
        for leaf1 in leaves:
            for leaf2 in leaves:
                if leaf1 != leaf2 and leaf1.markerid == leaf2.markerid:
                    if leaf1.turn_created == leaf2.turn_created:
                        raise ValueError(
                          "Two leaf nodes with same markerid and turn")
                    elif leaf1.turn_created < leaf2.turn_created:
                        prune_these.add(leaf1)
                    else:
                        prune_these.add(leaf2)
        for leaf in prune_these:
            leaves.remove(leaf)

        return leaves

    def print_leaves(self, newlines=True):
        """Print all childless nodes in tree, in string order."""
        leaves = self.get_leaves()
        leaves.sort(key=str)
        if newlines:
            print
        for leaf in leaves:
            print leaf
        if newlines:
            print

    def print_nodes(self, newlines=True):
        """Print all nodes in tree, in string order."""
        nodes = self.get_nodes()
        nodes.sort(key=Node.sort_key)
        if newlines:
            print
        for node in nodes:
            print node
        if newlines:
            print

    def get_leaf(self, markerid):
        """Return the leaf node with matching markerid"""
        leaves = self.get_leaves()
        for leaf in leaves:
            if leaf.markerid == markerid:
                return leaf
        return None

    @property
    def num_uncertain_legions(self):
        """Return the number of uncertain legions."""
        count = 0
        for node in self.get_leaves():
            if not node.all_certain:
                count += 1
        return count


class AllPredictSplits(list):
    """List of PredictSplits objects, for convenient testing."""
    def __init__(self):
        super(AllPredictSplits, self).__init__()

    def get_leaf(self, markerid):
        """Return the leaf with markerid, or None."""
        for ps in self:
            leaf = ps.get_leaf(markerid)
            if leaf:
                return leaf
        return None

    def print_leaves(self):
        """Print all leaf nodes."""
        print
        for ps in self:
            ps.print_leaves(False)
        print

    def print_nodes(self):
        """Print all nodes."""
        print
        for ps in self:
            ps.print_nodes(False)
        print

    def check(self):
        """Sanity check"""
        for ps in self:
            assert ps.num_uncertain_legions != 1
