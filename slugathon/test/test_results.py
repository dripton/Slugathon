__copyright__ = "Copyright (c) 2012 David Ripton"
__license__ = "GNU GPL v2"


import tempfile

from slugathon.net import Results


def test_db_creation():
    with tempfile.NamedTemporaryFile(prefix="slugathon", suffix=".db",
      delete=False) as tmp_file:
        tmp_path = tmp_file.name
    results = Results.Results(db_path=tmp_path)
