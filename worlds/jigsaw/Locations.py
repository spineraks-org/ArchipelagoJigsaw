import typing

from BaseClasses import Location

class LocData(typing.NamedTuple):
    id: int
    region: str


class JigsawLocation(Location):
    game: str = "Jigsaw"

    def __init__(self, player: int, name: str, nmatches: int, address: typing.Optional[int], parent):
        super().__init__(player, name, address, parent)
        self.nmatches = nmatches

location_table = {f"Connect {i} Pieces": LocData(234782000 + i, "Board") for i in range(2, 1601)}