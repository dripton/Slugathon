"""Raw data about player colors."""

name_to_abbrev = {
    "Black": "Bk",
    "Blue":  "Bu",
    "Brown": "Br",
    "Gold":  "Gd",
    "Green": "Gr",
    "Red":   "Rd",
}

abbrev_to_name = {}
for (name, abbrev) in name_to_abbrev.items():
    abbrev_to_name[abbrev] = name

colors = name_to_abbrev.keys()
colors.sort()

abbrevs = abbrev_to_name.keys()
abbrevs.sort()
