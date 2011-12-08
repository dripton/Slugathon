__copyright__ = "Copyright (c) 2003-2011 David Ripton"
__license__ = "GNU GPL v2"


"""Raw data about creature types.

name: (plural, power, skill, rangestrikes, flies, character_type,
  summonable, acquirable_every, count, color)

rangestrikes 0:no, 1:normal, 2:magic missile
"""

data = {

"Angel": ("Angels", 6, 4, 0, 1, "lord", 1, 100, 18, "by_player"),
"Archangel": ("Archangels", 9, 4, 0, 1, "lord", 1, 500, 6, "hydra_orange"),
"Behemoth": ("Behemoths", 8, 3, 0, 0, "creature", 0, 0, 18, "behemoth_green"),
"Centaur": ("Centaurs", 3, 4, 0, 0, "creature", 0, 0, 25, "centaur_gold"),
"Colossus": ("Colossi", 10, 4, 0, 0, "creature", 0, 0, 10, "colossus_pink"),
"Cyclops": ("Cyclopes", 9, 2, 0, 0, "creature", 0, 0, 28, "behemoth_green"),
"Dragon": ("Dragons", 9, 3, 1, 1, "creature", 0, 0, 18, "red"),
"Gargoyle": ("Gargoyles", 4, 3, 0, 1, "creature", 0, 0, 21, "black"),
"Giant": ("Giants", 7, 4, 1, 0, "creature", 0, 0, 18, "giant_blue"),
"Gorgon": ("Gorgons", 6, 3, 1, 1, "creature", 0, 0, 25, "black"),
"Griffon": ("Griffons", 5, 4, 0, 1, "creature", 0, 0, 18, "hydra_orange"),
"Guardian": ("Guardians", 12, 2, 0, 1, "demilord", 0, 0, 6, "colossus_pink"),
"Hydra": ("Hydrae", 10, 3, 1, 0, "creature", 0, 0, 10, "hydra_orange"),
"Lion": ("Lions", 5, 3, 0, 0, "creature", 0, 0, 28, "red"),
"Minotaur": ("Minotaurs", 4, 4, 1, 0, "creature", 0, 0, 21, "ogre_red"),
"Ogre": ("Ogres", 6, 2, 0, 0, "creature", 0, 0, 25, "ogre_red"),
"Ranger": ("Rangers", 4, 4, 1, 1, "creature", 0, 0, 28, "colossus_pink"),
"Serpent": ("Serpents", 18, 2, 0, 0, "creature", 0, 0, 10, "hydra_orange"),
"Titan": ("Titans", 6, 4, 0, 0, "lord", 0, 0, 6, "by_player"),
"Troll": ("Trolls", 8, 2, 0, 0, "creature", 0, 0, 28, "giant_blue"),
"Unicorn": ("Unicorns", 6, 4, 0, 0, "creature", 0, 0, 12, "hydra_orange"),
"Warbear": ("Warbears", 6, 3, 0, 0, "creature", 0, 0, 21, "centaur_gold"),
"Warlock": ("Warlocks", 5, 4, 2, 0, "demilord", 0, 0, 6, "hydra_orange"),
"Wyvern": ("Wyverns", 7, 3, 0, 1, "creature", 0, 0, 18, "colossus_pink"),

"Unknown": ("Unknowns", 6, 2, 0, 0, "unknown", 0, 0, 99, "black"),
}

starting_creature_names = ("Titan", "Angel", "Ogre", "Ogre", "Centaur",
  "Centaur", "Gargoyle", "Gargoyle")
