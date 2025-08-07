import json
import sys
sys.path.append("src/proxy")

from proxydatabase import *

data = [
    ("server", ServerEntry("127.0.0.1", "389", "", "", "")),
    ("user", UserEntry("user", "pass", True)),
    ("client", ClientEntry("dn", "pass")),
]

for t, e in data:
    with open(f"tests/schemas/{t}_python.json", "w") as f:
        json.dump(e.to_object(), f)
