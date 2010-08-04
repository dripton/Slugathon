__copyright__ = "Copyright (c) 2004-2008 David Ripton"
__license__ = "GNU GPL v2"


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
for (name, abbrev) in name_to_abbrev.iteritems():
    abbrev_to_name[abbrev] = name
del name, abbrev

colors = sorted(name_to_abbrev.iterkeys())

abbrevs = sorted(abbrev_to_name.iterkeys())
