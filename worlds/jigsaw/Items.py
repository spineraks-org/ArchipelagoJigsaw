import typing


from BaseClasses import Item, ItemClassification

class ItemData(typing.NamedTuple):
    code: typing.Optional[int]
    classification: ItemClassification

class JigsawItem(Item):
    game: str = "Jigsaw"

item_table = {f"Puzzle Piece {i}": ItemData(234782000+i, ItemClassification.progression) for i in range(1, 1601)}
item_table["Squawks"] = ItemData(234781999, ItemClassification.filler)
