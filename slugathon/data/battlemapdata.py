__copyright__ = "Copyright (c) 2005-2011 David Ripton"
__license__ = "GNU GPL v2"

"""Static battle map data"""

"""
{
    master terrain type: {
        hexlabel: (battle terrain type, elevation, { (hexside: border type) },
    }
}

Omitted hexes default to Plain, elevation 0, no borders
"""

data = {
    "Brush": {
        "A3": ("Bramble", 0, {}),
        "B2": ("Bramble", 0, {}),
        "C4": ("Bramble", 0, {}),
        "D1": ("Bramble", 0, {}),
        "D2": ("Bramble", 0, {}),
        "D5": ("Bramble", 0, {}),
        "E3": ("Bramble", 0, {}),
        "F4": ("Bramble", 0, {}),
    },

    "Desert": {
        "A1": ("Sand", 0, {}),
        "A2": ("Sand", 0, {0: "Dune", 1: "Dune"}),
        "B2": ("Sand", 0, {0: "Dune", 1: "Dune", 2: "Dune", 3: "Cliff"}),
        "D1": ("Sand", 0, {0: "Dune", 5: "Dune"}),
        "D4": ("Sand", 0, {2: "Dune", 3: "Cliff", 4: "Cliff", 5: "Dune"}),
        "D5": ("Sand", 0, {4: "Dune"}),
        "D6": ("Sand", 0, {}),
        "E1": ("Sand", 0, {0: "Cliff", 1: "Dune", 5: "Dune"}),
        "E4": ("Sand", 0, {2: "Dune", 3: "Dune"}),
        "E5": ("Sand", 0, {}),
        "F4": ("Sand", 0, {}),
    },

    "Hills": {
        "B1": ("Plain", 1, {0: "Slope", 1: "Slope", 2: "Slope", 5: "Slope"}),
        "B3": ("Plain", 1, {0: "Slope", 1: "Slope", 2: "Slope", 3: "Slope",
          4: "Slope", 5: "Slope"}),
        "C2": ("Tree", 1, {}),
        "C4": ("Tree", 1, {}),
        "D2": ("Plain", 1, {0: "Slope", 1: "Slope", 2: "Slope", 3: "Slope",
          4: "Slope", 5: "Slope"}),
        "D6": ("Plain", 1, {2: "Slope", 3: "Slope", 4: "Slope"}),
        "E3": ("Plain", 1, {0: "Slope", 1: "Slope", 2: "Slope", 3: "Slope",
          4: "Slope", 5: "Slope"}),
        "F2": ("Tree", 1, {}),
    },

    "Jungle": {
        "A2": ("Bramble", 0, {}),
        "B4": ("Tree", 1, {}),
        "C1": ("Bramble", 0, {}),
        "C3": ("Bramble", 0, {}),
        "C5": ("Bramble", 0, {}),
        "D3": ("Tree", 1, {}),
        "D4": ("Bramble", 0, {}),
        "E2": ("Bramble", 0, {}),
        "F3": ("Tree", 1, {}),
        "F4": ("Bramble", 0, {}),
    },

    "Marsh": {
        "A3": ("Bog", 0, {}),
        "C2": ("Bog", 0, {}),
        "C3": ("Bog", 0, {}),
        "D5": ("Bog", 0, {}),
        "E1": ("Bog", 0, {}),
        "E3": ("Bog", 0, {}),
    },

    "Mountains": {
        "A1": ("Plain", 1, {0: "Slope"}),
        "B1": ("Plain", 2, {0: "Slope", 1: "Cliff", 2: "Slope", 5: "Slope"}),
        "B2": ("Plain", 1, {0: "Slope", 1: "Slope", 2: "Slope", 5: "Slope"}),
        "B4": ("Plain", 1, {3: "Slope", 4: "Slope"}),
        "C1": ("Plain", 1, {0: "Slope", 1: "Slope", 2: "Slope"}),
        "C4": ("Plain", 1, {3: "Slope", 4: "Slope"}),
        "C5": ("Plain", 2, {2: "Slope", 3: "Slope", 4: "Slope"}),
        "D3": ("Plain", 1, {2: "Slope", 3: "Slope", 4: "Slope", 5: "Slope"}),
        "D4": ("Volcano", 2, {0: "Slope", 1: "Slope", 2: "Slope", 3: "Slope",
          4: "Cliff", 5: "Slope"}),
        "D5": ("Plain", 1, {}),
        "D6": ("Plain", 2, {2: "Slope", 3: "Slope"}),
        "E3": ("Plain", 1, {3: "Slope"}),
        "E4": ("Plain", 1, {}),
        "E5": ("Plain", 1, {}),
        "F1": ("Plain", 1, {4: "Slope", 5: "Slope"}),
        "F2": ("Plain", 2, {0: "Slope", 3: "Slope", 4: "Cliff", 5: "Slope"}),
        "F3": ("Plain", 1, {}),
        "F4": ("Plain", 2, {3: "Slope", 4: "Slope", 5: "Slope"}),
    },

    "Plains": {
    },

    "Swamp": {
        "B2": ("Bog", 0, {}),
        "C2": ("Tree", 1, {}),
        "C4": ("Tree", 1, {}),
        "C5": ("Bog", 0, {}),
        "D1": ("Bog", 0, {}),
        "D3": ("Bog", 0, {}),
        "E4": ("Tree", 1, {}),
        "F2": ("Bog", 0, {}),
    },

    "Tower": {
        "C3": ("Tower", 1, {3: "Wall", 4: "Wall", 5: "Wall"}),
        "C4": ("Tower", 1, {0: "Wall", 4: "Wall", 5: "Wall"}),
        "D3": ("Tower", 1, {2: "Wall", 3: "Wall", 4: "Wall"}),
        "D4": ("Tower", 2, {0: "Wall", 1: "Wall", 2: "Wall", 3: "Wall",
          4: "Wall", 5: "Wall"}),
        "D5": ("Tower", 1, {0: "Wall", 1: "Wall", 5: "Wall"}),
        "E3": ("Tower", 1, {1: "Wall", 2: "Wall", 3: "Wall"}),
        "E4": ("Tower", 1, {0: "Wall", 1: "Wall", 2: "Wall"}),
    },

    "Tundra": {
        "A1": ("Drift", 0, {}),
        "B2": ("Drift", 0, {}),
        "C2": ("Drift", 0, {}),
        "C4": ("Drift", 0, {}),
        "C5": ("Drift", 0, {}),
        "D3": ("Drift", 0, {}),
        "E1": ("Drift", 0, {}),
        "E4": ("Drift", 0, {}),
        "F2": ("Drift", 0, {}),
    },

    "Woods": {
        "A3": ("Tree", 1, {}),
        "C3": ("Tree", 1, {}),
        "D1": ("Tree", 1, {}),
        "E3": ("Tree", 1, {}),
        "E5": ("Tree", 1, {}),
    },
}


"""{ master terrain type: [start hex labels] }"""

startlist = {
    "Tower": ["C3", "C4", "D3", "D4", "D5", "E3", "E4"],
}
