import math
from typing import Dict, TextIO

from BaseClasses import CollectionState, Entrance, Item, ItemClassification, Location, Region, Tutorial

from worlds.AutoWorld import WebWorld, World

from .Items import JigsawItem, item_table, item_groups
from .Locations import JigsawLocation, location_table

from .Options import JigsawOptions, OrientationOfImage, PieceOrder
from .Rules import add_piece


class JigsawWeb(WebWorld):
    tutorials = [
        Tutorial(
            "Multiworld Setup Guide",
            "A guide to setting up Jigsaw. This guide covers single-player, multiworld, and website.",
            "English",
            "setup_en.md",
            "setup/en",
            ["Spineraks"],
        )
    ]
    
    


class JigsawWorld(World):
    """
    Make a Jigsaw puzzle! But first you'll have to find your pieces.
    Connect the pieces to unlock more. Goal: solve the puzzle of course!
    """

    game: str = "Jigsaw"
    options_dataclass = JigsawOptions

    web = JigsawWeb()

    item_name_to_id = {name: data.code for name, data in item_table.items()}

    location_name_to_id = {name: data.id for name, data in location_table.items()}
    
    item_name_groups = item_groups
    
    ap_world_version = "0.0.2"

    def _get_jigsaw_data(self):
        return {
            # "world_seed": self.multiworld.per_slot_randoms[self.player].getrandbits(32),
            "seed_name": self.multiworld.seed_name,
            "player_name": self.multiworld.get_player_name(self.player),
            "player_id": self.player,
            "race": self.multiworld.is_race,
        }
        
    def calculate_optimal_nx_and_ny(self, number_of_pieces, orientation):
        def mround(x):
            return int(round(x))

        def msqrt(x):
            return math.sqrt(x)

        def mabs(x):
            return abs(x)
        
        height = 1
        width = orientation

        nHPieces = mround(msqrt(number_of_pieces * width / height))
        nVPieces = mround(number_of_pieces / nHPieces)
        
        errmin = float('inf')
        optimal_nx, optimal_ny = nHPieces, nVPieces

        for ky in range(5):
            ncv = nVPieces + ky - 2
            for kx in range(5):
                nch = nHPieces + kx - 2
                err = nch * height / ncv / width
                err = (err + 1 / err) - 2  # error on pieces dimensions ratio
                err += mabs(1 - nch * ncv / number_of_pieces)  # adds error on number of pieces

                if err < errmin:  # keep smallest error
                    errmin = err
                    optimal_nx, optimal_ny = nch, ncv

        return optimal_nx, optimal_ny
        
    def generate_early(self):       
        self.orientation = 1
        if self.options.orientation_of_image == OrientationOfImage.option_landscape:
            self.orientation = 1.5
        if self.options.orientation_of_image == OrientationOfImage.option_portrait:
            self.orientation = 0.8
        self.nx, self.ny = self.calculate_optimal_nx_and_ny(self.options.number_of_pieces.value, self.orientation)
        self.npieces = self.nx * self.ny
        
        pieces = [i for i in range(1, self.npieces + 1)]
        self.multiworld.random.shuffle(pieces)
        
        merges = 0
        clusters = []
        
        self.precollected_pieces = []
        self.itempool_pieces = []
        
        while pieces:  # pieces left
            p = None
            if self.options.piece_order == PieceOrder.option_random_order:
                p = pieces.pop(0)  # pick the first remaining piece
            if self.options.piece_order == PieceOrder.option_corners_edges_rest:
                # Check for corner pieces
                for corner in [1, self.nx, self.nx * (self.ny - 1) + 1, self.nx * self.ny]:
                    if corner in pieces:
                        p = corner
                        pieces.remove(corner)
                        break
                else:
                    # Check for edge pieces
                    for edge in pieces:
                        if edge <= self.nx or edge > self.nx * (self.ny - 1) or edge % self.nx <= 1:
                            p = edge
                            pieces.remove(edge)
                            break
                    else:
                        # If no corner or edge pieces, pick the first remaining piece
                        p = pieces.pop(0)
            
            # if you have merges left to unlock pieces
            if merges > len(self.itempool_pieces) + self.options.number_of_checks_out_of_logic.value:
                self.itempool_pieces.append(p)  # add piece to itempool. The order in this is the order you'll get pcs
            else:
                self.precollected_pieces.append(p)  # if no merges left, add piece to start_inventory
                
            clusters, merges = add_piece(clusters, p, self.nx, self.ny)  # update number of merges left
                    
        self.possible_merges = [- self.options.number_of_checks_out_of_logic.value]
        self.actual_possible_merges = [0]
        merges = 0
        clusters = []
        
        for p in self.precollected_pieces:
            clusters, merges = add_piece(clusters, p, self.nx, self.ny)
            self.possible_merges.append(merges - self.options.number_of_checks_out_of_logic.value) 
            self.actual_possible_merges.append(merges)
        for c, p in enumerate(self.itempool_pieces):
            clusters, merges = add_piece(clusters, p, self.nx, self.ny)
            if len(self.itempool_pieces) - c < 10:
                self.possible_merges.append(merges)   
            else:
                self.possible_merges.append(merges - self.options.number_of_checks_out_of_logic.value)   
            self.actual_possible_merges.append(merges)
        
        self.pieces_needed_per_merge = [0]
        for i in range(1, self.npieces):
            self.pieces_needed_per_merge.append(next(index for index, value in enumerate(self.possible_merges) if value >= i))
        
        print(self.precollected_pieces)
        print(self.possible_merges)
        print(self.pieces_needed_per_merge)
        
        pieces_left = math.ceil(len(self.itempool_pieces) * (1 + self.options.percentage_of_extra_pieces.value / 100))
                
                
        if pieces_left / (self.npieces - 2) < 1:
            self.pool_pieces = [f"Puzzle Piece" for i in range(pieces_left)]                
        else:
            self.pool_pieces = []
            number_of_locations_left = self.npieces - 2
            while number_of_locations_left > 0:
                n = math.ceil(pieces_left / number_of_locations_left)
                if n > 2:
                    exit("[Jigsaw] Did not account for n > 2...")
                self.pool_pieces.append(f"{str(n) + ' ' if n > 1 else ''}Puzzle Piece{'s' if n > 1 else ''}")
                number_of_locations_left -= 1
                pieces_left -= n
                
        for _ in self.precollected_pieces:
            self.multiworld.push_precollected(self.create_item(f"Puzzle Piece"))
            
        self.pool_pieces += ["Squawks"] * (self.npieces - len(self.pool_pieces) - 2)
            

    def create_items(self):
        self.multiworld.itempool += [self.create_item(name) for name in self.pool_pieces]

    def create_regions(self):        
        # simple menu-board construction
        menu = Region("Menu", self.player, self.multiworld)
        board = Region("Board", self.player, self.multiworld)

        # add locations to board, one for every location in the location_table
        board.locations = [
            JigsawLocation(self.player, f"Merge {i} times", 234782000+i, i, board)
            for i in range(1, self.npieces)
        ]
        
        # self.possible_merges is a list, and self.possible_merges[x] is the number of merges you can make with x puzzle pieces
        for loc in board.locations:
            # loc.nmerges is the number of merges for that location. So "Merge 4 times" has nmerges equal to 4
            loc.access_rule = lambda state, count=loc.nmerges: \
                state.count("Puzzle Piece", self.player) + 2 * state.count("2 Puzzle Pieces", self.player) >= self.pieces_needed_per_merge[count]
            
        # Change the victory location to an event and place the Victory item there.
        victory_location_name = f"Merge {self.npieces - 1} times"
        self.get_location(victory_location_name).address = None
        self.get_location(victory_location_name).place_locked_item(
            Item("Victory", ItemClassification.progression, None, self.player)
        )
        
        self.multiworld.completion_condition[self.player] = lambda state: state.has("Victory", self.player)

        # add the regions
        connection = Entrance(self.player, "New Board", menu)
        menu.exits.append(connection)
        connection.connect(board)
        self.multiworld.regions += [menu, board]

    def get_filler_item_name(self) -> str:
        return "Squawks"

    def create_item(self, name: str) -> Item:
        item_data = item_table[name]
        item = JigsawItem(name, item_data.classification, item_data.code, self.player)
        return item

    def fill_slot_data(self):
        """
        make slot data, which consists of jigsaw_data, options, and some other variables.
        """
        slot_data = self._get_jigsaw_data()
        
        slot_data["orientation"] = self.orientation
        slot_data["nx"] = self.nx
        slot_data["ny"] = self.ny
        slot_data["piece_order"] = self.precollected_pieces + self.itempool_pieces
        slot_data["possible_merges"] = self.possible_merges
        slot_data["actual_possible_merges"] = self.actual_possible_merges
        return slot_data

    def write_spoiler(self, spoiler_handle: TextIO) -> None:
        spoiler_handle.write(f"\nPuzzle dimension {self.nx} {self.ny}\n")
        spoiler_handle.write(f"\nself.precollected_pieces {self.precollected_pieces}\n")
        spoiler_handle.write(f"\nself.itempool_pieces {self.itempool_pieces}\n")
        spoiler_handle.write(f"\nself.possible_merges {self.possible_merges}\n")
        spoiler_handle.write(f"\nself.actual_possible_merges {self.actual_possible_merges}\n")
        spoiler_handle.write(f"\nself.pieces_needed_per_merge {self.pieces_needed_per_merge}\n")