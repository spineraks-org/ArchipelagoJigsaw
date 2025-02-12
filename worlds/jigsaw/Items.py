import typing


from BaseClasses import Item, ItemClassification
from typing import Optional

class ItemData(typing.NamedTuple):
    code: typing.Optional[int]
    classification: ItemClassification
    piece_nr: int

class JigsawItem(Item):
    game: str = "Jigsaw"
    
    def __init__(self, name: str, classification: ItemClassification, code: Optional[int], player: int, piece_nr: int):
        self.name = name
        self.classification = classification
        self.player = player
        self.code = code
        self.location = None
        self.piece_nr = piece_nr

item_table = {f"Puzzle Piece {i}": ItemData(234782000+i, ItemClassification.progression_skip_balancing, i) for i in range(1, 1601)}
item_table["Squawks"] = ItemData(234781999, ItemClassification.filler, -111111)

# item groups for better hinting
item_groups = {
    "Pieces": {f"Puzzle Piece {i}" for i in range(1, 1601)},
}
