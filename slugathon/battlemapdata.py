"""Static battle map data

{
    master terrain type: {
        hexlabel: (battle terrain type, elevation, { (hexside: border type) },
    }
}

Omitted hexes default to Plains, elevation 0, no borders
"""

data = {
    "Brush": {
        "A1": ("Bramble", 0, {}),
        "B3": ("Bramble", 0, {}),
        "C2": ("Bramble", 0, {}),
        "D2": ("Bramble", 0, {}),
        "D5": ("Bramble", 0, {}),
        "D6": ("Bramble", 0, {}),
        "E3": ("Bramble", 0, {}),
        "F1": ("Bramble", 0, {}),
    }, 

    "Desert": {
        "A2": ("Sand", 0, {0: "Dune", 1: "Dune"}),
        "A3": ("Sand", 0, {}),
        "B3": ("Sand", 0, {0: "Dune", 1: "Dune", 2: "Dune", 3: "Cliff"}),
        "D1": ("Sand", 0, {}),
        "D2": ("Sand", 0, {4: "Dune"}),
        "D3": ("Sand", 0, {2: "Dune", 3: "Cliff", 4: "Cliff", 5: "Dune"}),
        "D6": ("Sand", 0, {0: "Dune", 5: "Dune"}),
        "E1": ("Sand", 0, {}),
        "E2": ("Sand", 0, {2: "Dune", 3: "Dune"}),
        "E5": ("Sand", 0, {0: "Cliff", 1: "Dune", 5: "Dune"}),
        "F1": ("Sand", 0, {}),
    },

    "Hills": {
        "B2": ("Plains", 1, {0: "Slope", 1: "Slope", 2: "Slope", 3: "Slope", 
          4: "Slope", 5: "Slope"}),
        "B4": ("Plains", 1, {0: "Slope", 1: "Slope", 2: "Slope", 5: "Slope"}),
        "C2": ("Tree", 1, {}),
        "C4": ("Tree", 1, {}),
        "D1": ("Plains", 1, {2: "Slope", 3: "Slope", 4: "Slope"}),
        "D5": ("Plains", 1, {0: "Slope", 1: "Slope", 2: "Slope", 3: "Slope", 
          4: "Slope", 5: "Slope"}),
        "F3": ("Tree", 1, {}),
    },

    "Jungle": {
        "A2": ("Bramble", 0, {}),
        "B1": ("Tree", 1, {}),
        "C1": ("Bramble", 0, {}),
        "C3": ("Bramble", 0, {}),
        "C5": ("Bramble", 0, {}),
        "D3": ("Bramble", 0, {}),
        "D4": ("Tree", 1, {}),
        "E4": ("Bramble", 0, {}),
        "F1": ("Bramble", 0, {}),
        "F2": ("Tree", 1, {}),
    },

    "Marsh": {
        "A1": ("Bog", 0, {}),
        "C3": ("Bog", 0, {}),
        "C4": ("Bog", 0, {}),
        "D2": ("Bog", 0, {}),
        "E3": ("Bog", 0, {}),
        "E5": ("Bog", 0, {}),
    },

    "Mountains": {
        "A3": ("Plains", 1, {0: "Slope"}),
        "B1": ("Plains", 1, {3: "Slope", 4: "Slope"}),
        "B3": ("Plains", 1, {0: "Slope", 1: "Slope", 2: "Slope", 5: "Slope"}),
        "B4": ("Plains", 2, {0: "Slope", 1: "Cliff", 2: "Slope", 5: "Slope"}),
        "C1": ("Plains", 2, {2: "Slope", 3: "Slope", 4: "Slope"}),
        "C2": ("Plains", 1, {3: "Slope", 4: "Slope"}),
        "C5": ("Plains", 1, {0: "Slope", 1: "Slope", 2: "Slope"}),
        "D1": ("Plains", 2, {2: "Slope", 3: "Slope"}),
        "D2": ("Plains", 1, {}),
        "D3": ("Volcano", 2, {0: "Slope", 1: "Slope", 2: "Slope", 3: "Slope", 
          4: "Cliff", 5: "Slope"}),
        "D4": ("Plains", 1, {2: "Slope", 3: "Slope", 4: "Slope", 5: "Slope"}),
        "E1": ("Plains", 1, {}),
        "E2": ("Plains", 1, {}),
        "E3": ("Plains", 1, {3: "Slope"}),
        "F1": ("Plains", 2, {3: "Slope", 4: "Slope", 5: "Slope"}),
        "F2": ("Plains", 1, {}),
        "F4": ("Plains", 1, {4: "Slope", 5: "Slope"}),
    },

    "Plains": {
    },

    "Swamp": {
        "B3": ("Bog", 0, {}),
        "C1": ("Bog", 0, {}),
        "C2": ("Tree", 1, {}),
        "C4": ("Tree", 1, {}),
        "D4": ("Bog", 0, {}),
        "D6": ("Bog", 0, {}),
        "E2": ("Tree", 1, {}),
        "F3": ("Bog", 0, {}),
    },

    "Tower": {
        "C2": ("Tower", 1, {0: "Wall", 4: "Wall", 5: "Wall"}),
        "C3": ("Tower", 1, {3: "Wall", 4: "Wall", 5: "Wall"}),
        "D2": ("Tower", 1, {0: "Wall", 1: "Wall", 5: "Wall"}),
        "D3": ("Tower", 2, {0: "Wall", 1: "Wall", 2: "Wall", 3: "Wall", 
          4: "Wall", 5: "Wall"}),
        "D4": ("Tower", 1, {2: "Wall", 3: "Wall", 4: "Wall"}), 
        "E2": ("Tower", 1, {0: "Wall", 1: "Wall", 2: "Wall"}), 
        "E3": ("Tower", 1, {1: "Wall", 2: "Wall", 3: "Wall"}), 
    },

    "Tundra": {
        "A3": ("Drift", 0, {}),
        "B3": ("Drift", 0, {}),
        "C1": ("Drift", 0, {}),
        "C2": ("Drift", 0, {}),
        "C4": ("Drift", 0, {}),
        "D4": ("Drift", 0, {}),
        "E2": ("Drift", 0, {}),
        "E5": ("Drift", 0, {}),
        "F3": ("Drift", 0, {}),
    },

    "Woods": {
        "A1": ("Tree", 1, {}),
        "C3": ("Tree", 1, {}),
        "D6": ("Tree", 1, {}),
        "E1": ("Tree", 1, {}),
        "E3": ("Tree", 1, {}),
    },
}
