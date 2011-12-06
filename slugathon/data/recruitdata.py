__copyright__ = "Copyright (c) 2005-2011 David Ripton"
__license__ = "GNU GPL v2"


"""Static recruiting data

Terrain type to list of tuples, (creature_name, num_to_recruit)

Lowercase creature_names are special.  "anything" means anything.
"creature" means anything with character_type of "creature"

Any non-special creature_name with num_to_recruit >= 1 can be
recruited with one of the same type of creature, >= 1 of any
creature later in the list, or num_to_recruit of the preceding
creature_name.

An empty tuple in the list is a break.  Neither up- or
down-recruiting can cross a break.
"""

ANYTHING = "anything"
CREATURE = "creature"

data = {
    "Brush": [("Gargoyle", 1), ("Cyclops", 2), ("Gorgon", 2)],

    "Desert": [("Lion", 1), ("Griffon", 3), ("Hydra", 2)],

    "Hills": [("Ogre", 1), ("Minotaur", 3), ("Unicorn", 2)],

    "Jungle": [("Gargoyle", 1), ("Cyclops", 2), ("Behemoth", 3),
      ("Serpent", 2)],

    "Marsh": [("Ogre", 1), ("Troll", 2), ("Ranger", 2)],

    "Mountains": [("Lion", 1), ("Minotaur", 2), ("Dragon", 2),
      ("Colossus", 2)],

    "Plains": [("Centaur", 1), ("Lion", 2), ("Ranger", 2)],

    "Swamp": [("Troll", 1), ("Wyvern", 3), ("Hydra", 2)],

    "Tower": [(ANYTHING, 0), ("Centaur", 1),
              (),
              (ANYTHING, 0), ("Gargoyle", 1),
              (),
              (ANYTHING, 0), ("Ogre", 1),
              (),
              (CREATURE, 0), ("Guardian", 3),
              (),
              ("Titan", 0), ("Warlock", 1)],

    "Tundra": [("Troll", 1), ("Warbear", 2), ("Giant", 2), ("Colossus", 2)],

    "Woods": [("Centaur", 1), ("Warbear", 3), ("Unicorn", 2)],
}
