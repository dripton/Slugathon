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
        "A1": ("Brambles", 0, {}),
        "B3": ("Brambles", 0, {}),
        "C2": ("Brambles", 0, {}),
        "D2": ("Brambles", 0, {}),
        "D5": ("Brambles", 0, {}),
        "D6": ("Brambles", 0, {}),
        "E3": ("Brambles", 0, {}),
        "F1": ("Brambles", 0, {}),
    }, 

    "Desert": {
        "A2": ("Sand", 0, {0: "d", 1: "d"}),
        "A3": ("Sand", 0, {}),
        "B3": ("Sand", 0, {0: "d", 1: "d", 2: "d", 3: "c"}),
        "D1": ("Sand", 0, {}),
        "D2": ("Sand", 0, {4: "d"}),
        "D3": ("Sand", 0, {2: "d", 3: "c", 4: "c", 5: "d"}),
        "D6": ("Sand", 0, {0: "d", 5: "d"}),
        "E1": ("Sand", 0, {}),
        "E2": ("Sand", 0, {2: "d", 3: "d"}),
        "E5": ("Sand", 0, {0: "c", 1: "d", 5: "d"}),
        "F1": ("Sand", 0, {}),
    },

    "Hills": {
        "B2": ("Plains", 1, {0: "s", 1: "s", 2: "s", 3: "s", 4: "s", 5: "s"}),
        "B4": ("Plains", 1, {0: "s", 1: "s", 2: "s", 5: "s"}),
        "C2": ("Tree", 1, {}),
        "C4": ("Tree", 1, {}),
        "D1": ("Plains", 1, {2: "s", 3: "s", 4: "s"}),
        "D5": ("Plains", 1, {0: "s", 1: "s", 2: "s", 3: "s", 4: "s", 5: "s"}),
        "F3": ("Tree", 1, {}),
    },

    "Jungle": {
        "A2": ("Brambles", 0, {}),
        "B1": ("Tree", 1, {}),
        "C1": ("Brambles", 0, {}),
        "C3": ("Brambles", 0, {}),
        "C5": ("Brambles", 0, {}),
        "D3": ("Brambles", 0, {}),
        "D4": ("Tree", 1, {}),
        "E4": ("Brambles", 0, {}),
        "F1": ("Brambles", 0, {}),
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
        "A3": ("Plains", 1, {0: "s"}),
        "B1": ("Plains", 1, {3: "s", 4: "s"}),
        "B3": ("Plains", 1, {0: "s", 1: "s", 2: "s", 5: "s"}),
        "B4": ("Plains", 2, {0: "s", 1: "c", 2: "s", 5: "s"}),
        "C1": ("Plains", 2, {2: "s", 3: "s", 4: "s"}),
        "C2": ("Plains", 1, {3: "s", 4: "s"}),
        "C5": ("Plains", 1, {0: "s", 1: "s", 2: "s"}),
        "D1": ("Plains", 2, {2: "s", 3: "s"}),
        "D2": ("Plains", 1, {}),
        "D3": ("Volcano", 2, {0: "s", 1: "s", 2: "s", 3: "s", 4: "c", 5: "s"}),
        "D4": ("Plains", 1, {2: "s", 3: "s", 4: "s", 5: "s"}),
        "E1": ("Plains", 1, {}),
        "E2": ("Plains", 1, {}),
        "E3": ("Plains", 1, {3: "s"}),
        "F1": ("Plains", 2, {3: "s", 4: "s", 5: "s"}),
        "F2": ("Plains", 1, {}),
        "F4": ("Plains", 1, {4: "s", 5: "s"}),
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
        "C2": ("Tower", 1, {0: "w", 4: "w", 5: "w"}),
        "C3": ("Tower", 1, {3: "w", 4: "w", 5: "w"}),
        "D2": ("Tower", 1, {0: "w", 1: "w", 5: "w"}),
        "D3": ("Tower", 2, {0: "w", 1: "w", 2: "w", 3: "w", 4: "w", 5: "w"}),
        "D4": ("Tower", 1, {2: "w", 3: "w", 4: "w"}), 
        "E2": ("Tower", 1, {0: "w", 1: "w", 2: "w"}), 
        "E3": ("Tower", 1, {1: "w", 2: "w", 3: "w"}), 
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
