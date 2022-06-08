"""
This simple script holds the control flow to map from keywords in the SRA
sample text to specific .bed files. These .bed files specify the primers to be
trimmed from the sample's short reads.
"""

import json

d = {
    "ArticV4.1": "data/articv4.1.bed",
    "ArticV4": "data/articv4.bed",
    "NEBNext": {
        "VarSkip": {
            "Long": "data/NEBNextVSL.bed",
            "V2": "data/NEBNextVSSv2.bed",
            "Other": "data/NEBNextVSS.bed",
        },
        "Other": "data/articv3.bed",
    },
    "Artic": "data/articv3.bed",
    "QiaSeq": "data/QiaSeq.bed",
    "SNAPadd": "data/SNAPaddtlCov.bed",
    "SNAP": "data/SNAP.bed",
    "Spike-Amps": "data/SpikeSeq.bed",
    "IonAmpliSeq": "Unknown",  # "data/IonAmpliSeq.bed" Seems to not be used
    "Paragon": "Unknown",
}  # "data/Paragon.bed" Used by one USA group

j = json.dumps(d, indent=4)

with open("data/bed_mapping.json", "w", encoding="utf-8") as outfile:
    outfile.write(j)
