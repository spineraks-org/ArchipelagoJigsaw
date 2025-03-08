import typing


from BaseClasses import Item, ItemClassification
from typing import Optional

class ItemData(typing.NamedTuple):
    code: typing.Optional[int]
    classification: ItemClassification

class JigsawItem(Item):
    game: str = "Jigsaw"
    
    def __init__(self, name: str, classification: ItemClassification, code: Optional[int], player: int):
        self.name = name
        self.classification = classification
        self.player = player
        self.code = code
        self.location = None

item_table = {
    "Puzzle Piece": ItemData(234782000, ItemClassification.progression_skip_balancing),
    "2 Puzzle Pieces": ItemData(234782001, ItemClassification.progression_skip_balancing),
    "5 Puzzle Pieces": ItemData(234782004, ItemClassification.progression_skip_balancing),
    "10 Puzzle Pieces": ItemData(234782009, ItemClassification.progression_skip_balancing),
    "Squawks": ItemData(234781999, ItemClassification.filler),
}

item_groups = {
    "Puzzle Pieces": {
        "Puzzle Piece", 
        "2 Puzzle Pieces",
        "5 Puzzle Pieces",
        "10 Puzzle Pieces"
    }
}