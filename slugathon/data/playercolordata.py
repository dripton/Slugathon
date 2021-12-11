from typing import Dict, List


__copyright__ = "Copyright (c) 2004-2008 David Ripton"
__license__ = "GNU GPL v2"


"""Raw data about player colors."""


name_to_abbrev = {
    "Black": "Bk",
    "Blue": "Bu",
    "Brown": "Br",
    "Gold": "Gd",
    "Green": "Gr",
    "Red": "Rd",
}  # type: Dict[str, str]

abbrev_to_name = {}  # type: Dict[str, str]
for (name, abbrev) in name_to_abbrev.items():
    abbrev_to_name[abbrev] = name
del name, abbrev

colors = sorted(name_to_abbrev.keys())  # type: List[str]

abbrevs = sorted(abbrev_to_name.keys())  # type: List[str]
