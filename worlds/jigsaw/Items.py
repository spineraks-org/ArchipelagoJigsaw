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
    "Squawks": ItemData(234781999, ItemClassification.filler)
}
