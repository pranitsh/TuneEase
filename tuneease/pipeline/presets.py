prog_to_abrv = {
    "80": "M",
    "32": "B",
    "128": "D",
    "25": "G",
    "0": "P",
    "48": "S",
}
inst_to_row = {"80": 0, "32": 1, "128": 2, "25": 3, "0": 4, "48": 5, "129": 6}
track_name = {
    "M": "lead",
    "B": "bass",
    "D": "drum",
    "G": "guitar",
    "P": "piano",
    "S": "string",
}
prog_to_name = {
    "32": "Bass",
    "128": "Drums",
    "25": "Guitar",
    "0": "Grand_Piano",
    "48": "Strings",
}


class RootKinds:
    root_dict = None
    kind_dict = None
    root_list = None
    kind_list = None

    def __init__(self) -> None:
        self.root_dict = {
            "C": 0,
            "C#": 1,
            "D": 2,
            "Eb": 3,
            "E": 4,
            "F": 5,
            "F#": 6,
            "G": 7,
            "Ab": 8,
            "A": 9,
            "Bb": 10,
            "B": 11,
        }
        self.kind_dict = {
            "null": 0,
            "m": 1,
            "+": 2,
            "dim": 3,
            "seven": 4,
            "maj7": 5,
            "m7": 6,
            "m7b5": 7,
        }
        self.root_list = list(self.root_dict.keys())
        self.kind_list = list(self.kind_dict.keys())
