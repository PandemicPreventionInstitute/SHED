"""
This file saves the primer parsing logic as a json object to be deserialized
and parsed when generating the data data file.
"""

import json

d = {
    "SNAP": {"ADD": "SNAPadd", "Other": "SNAP"},
    "SWIFT": "SNAP",
    "QIASEQ": "QiaSeq",
    "NEBNEXT": {
        "VARSKIP": "NEBNext VarSkip",
        "LONG": "NEBNext Long",
        "SHORT": "NEBNext Short",
        "V2": "NEBNext V2",
    },
    "ARCTIC": {
        "V3": "ArcticV3",
        "V4.1": "ArcticV4.1",
        "V4": "Arcticv4",
        "Other": "Arctic",
    },
    "PRJNA715712": "Spike-Amps",
    "PRJNA748354": "Spike-Amps",
    "FISHER": "IonAmpliSeq",
    "ION AMPLISEQ": "IonAmpliSeq",
    "PARAGON": "Paragon",
}

j = json.dumps(d, indent=4)

with open("data/elements_mapping.json", "w", encoding="utf-8") as outfile:
    outfile.write(j)
