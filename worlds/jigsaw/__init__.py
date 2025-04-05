import math
from typing import Any, Dict, TextIO

from BaseClasses import CollectionState, Entrance, Item, ItemClassification, Location, Region, Tutorial

from worlds.AutoWorld import WebWorld, World

from .Items import JigsawItem, item_table, item_groups
from .Locations import JigsawLocation, location_table

from .Options import JigsawOptions, OrientationOfImage, PieceOrder, PieceTypeOrder, StrictnessPieceOrder
from .Rules import PuzzleBoard


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
    
    ap_world_version = "0.3.0"

    def _get_jigsaw_data(self):
        return {
            "seed_name": self.multiworld.seed_name,
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
        
        
        if self.options.piece_order_type == PieceTypeOrder.option_random_order:
            pieces_groups = [[i for i in range(1, self.npieces + 1)]]
            self.multiworld.random.shuffle(pieces_groups[0])
        else:
            corners = [1, self.nx, self.nx * (self.ny - 1) + 1, self.nx * self.ny]
            edges = [i for i in range(2, self.nx)] \
                    + [self.nx * (self.ny - 1) + i for i in range(2, self.nx)] \
                    + [1 + self.nx * i for i in range(1, self.ny - 1)] \
                    + [self.nx + self.nx * i for i in range(1, self.ny - 1)]
            normal = [i for i in range(1, self.npieces + 1) if i not in corners and i not in edges]
            self.multiworld.random.shuffle(corners)
            self.multiworld.random.shuffle(edges)
            self.multiworld.random.shuffle(normal)
            if self.options.piece_order_type == PieceTypeOrder.option_corners_edges_normal:
                pieces_groups = [corners, edges, normal]
            elif self.options.piece_order_type == PieceTypeOrder.option_normal_edges_corners:
                pieces_groups = [normal, edges, corners]
            elif self.options.piece_order_type == PieceTypeOrder.option_edges_normal_corners:
                pieces_groups = [edges, normal, corners]
            elif self.options.piece_order_type == PieceTypeOrder.option_corners_normal_edges:
                pieces_groups = [corners, normal, edges]
            elif self.options.piece_order_type == PieceTypeOrder.option_normal_corners_edges:
                pieces_groups = [normal, corners, edges]
            elif self.options.piece_order_type == PieceTypeOrder.option_edges_corners_normal:
                pieces_groups = [edges, corners, normal]
                
            move_pieces = (100 - self.options.strictness_piece_order_type.value) / 100

            def move_percentage(from_group, to_group, percentage):
                move_count = int(len(from_group) * percentage)
                for _ in range(move_count):
                    if from_group:
                        to_group.append(from_group.pop(0))

            if len(pieces_groups) > 2:
                move_percentage(pieces_groups[2], pieces_groups[1], move_pieces)
            if len(pieces_groups) > 1:
                move_percentage(pieces_groups[1], pieces_groups[0], move_pieces)
        
        for pieces in pieces_groups:
            self.multiworld.random.shuffle(pieces)
        
        board = PuzzleBoard(self.nx, self.ny)
        
        self.precollected_pieces = []
        self.itempool_pieces = []
        
        first_piece = True
        for pieces in pieces_groups:
            best_result_ever = 0
            while pieces:  # pieces left
                p = None
                
                if self.options.piece_order == PieceOrder.option_random_order:
                    p = pieces.pop(0)  # pick the first remaining piece
                    
                else:
                    if self.options.strictness_piece_order.value / 100 < self.random.random():
                        p = pieces.pop(0)
                    
                    elif self.options.piece_order == PieceOrder.option_every_piece_fits:
                        for p in pieces:
                            m = board.get_merges_from_adding_piece(p - 1)
                            if first_piece or m > 0:
                                pieces.remove(p)
                                break
                        else:
                            p = pieces.pop(0)
                        
                    elif self.options.piece_order == PieceOrder.option_least_merges_possible:
                        best_piece = None
                        best_result = 5
                        # This is a hot loop, so the code within it needs to be as performant as possible.
                        for p in pieces:
                            m = board.get_merges_from_adding_piece(p - 1)
                            if first_piece or m <= best_result_ever:
                                best_piece = p
                                best_result = 0
                                break
                            if m < best_result:
                                best_piece = p
                                best_result = m
                                
                        p = best_piece
                        best_result_ever = best_result
                        pieces.remove(p)                        
                    
                if p == None:
                    raise RuntimeError("Jigsaw: No piece selected")
                
                # if you have merges left to unlock pieces
                if board.merges_count > len(self.itempool_pieces) + self.options.number_of_checks_out_of_logic.value:
                    self.itempool_pieces.append(p)  # add piece to itempool. The order in this is the order you'll get pcs
                else:
                    self.precollected_pieces.append(p)  # if no merges left, add piece to start_inventory

                board.add_piece(p - 1)
                
                first_piece = False
                    
        self.possible_merges = [- self.options.number_of_checks_out_of_logic.value]
        self.actual_possible_merges = [0]
        board = PuzzleBoard(self.nx, self.ny)
        
        for p in self.precollected_pieces:
            board.add_piece(p - 1)
            merges = board.merges_count
            self.possible_merges.append(merges - self.options.number_of_checks_out_of_logic.value) 
            self.actual_possible_merges.append(merges)
        for c, p in enumerate(self.itempool_pieces):
            board.add_piece(p - 1)
            merges = board.merges_count
            if len(self.itempool_pieces) - c < 10:
                self.possible_merges.append(merges)   
            else:
                self.possible_merges.append(merges - self.options.number_of_checks_out_of_logic.value)   
            self.actual_possible_merges.append(merges)
        
        self.pieces_needed_per_merge = [0]
        for i in range(1, self.npieces):
            self.pieces_needed_per_merge.append(next(index for index, value in enumerate(self.possible_merges) if value >= i))
        
        pieces_left = math.ceil(len(self.itempool_pieces) * (1 + self.options.percentage_of_extra_pieces.value / 100))
        
        self.number_of_locations = min(
            int(self.options.percentage_of_merges_that_are_checks.value / 100 * (self.npieces - 2)),
            self.options.maximum_number_of_checks.value
        )
        
        if not self.options.allow_filler_items.value:
            self.number_of_locations = min(self.number_of_locations, pieces_left)
                
        if pieces_left / self.number_of_locations < 1:
            self.pool_pieces = [f"Puzzle Piece" for i in range(pieces_left)]                
        else:
            self.pool_pieces = []
            number_of_locations_left = self.number_of_locations
            while number_of_locations_left > 0 and pieces_left > 0:
                n = pieces_left / number_of_locations_left
                if n > 25:
                    n = 100
                elif n > 10:
                    n = 25
                elif n > 5:
                    n = 10
                elif n > 2:
                    n = 5
                elif n > 1:
                    n = 2
                else:
                    n = 1
                self.pool_pieces.append(f"{str(n) + ' ' if n > 1 else ''}Puzzle Piece{'s' if n > 1 else ''}")
                number_of_locations_left -= 1
                pieces_left -= n
            if pieces_left > 0:
                raise RuntimeError("[Jigsaw] Was not able to place all puzzle pieces...")
                
        pieces_from_start = len(self.precollected_pieces)
            
        while pieces_from_start > 0:
            if pieces_from_start >= 100:
                n = 100
            elif pieces_from_start >= 25:
                n = 25
            elif pieces_from_start >= 10:
                n = 10
            elif pieces_from_start >= 5:
                n = 5
            elif pieces_from_start >= 2:
                n = 2
            else:
                n = 1
            self.multiworld.push_precollected(self.create_item(f"{str(n) + ' ' if n > 1 else ''}Puzzle Piece{'s' if n > 1 else ''}"))
            pieces_from_start -= n
            
        self.pool_pieces += ["Squawks"] * (self.number_of_locations - len(self.pool_pieces))
            
    def create_items(self):
        self.multiworld.itempool += [self.create_item(name) for name in self.pool_pieces]

    def create_regions(self):        
        # simple menu-board construction
        menu = Region("Menu", self.player, self.multiworld)
        board = Region("Board", self.player, self.multiworld)
        
        max_score = self.npieces - 1
        scaling = 2  # parameter that determines how many low-score location there are.

        scores = []
        # the scores follow the function int( 1 + (percentage ** scaling) * (max_score-1) )
        # however, this will have many low values, sometimes repeating.
        # to avoid repeating scores, highest_score keeps tracks of the highest score location
        # and the next score will always be at least highest_score + 1
        # note that current_score is at most max_score-1
        highest_score = 0
        start_score = 0

        for i in range(self.number_of_locations):
            percentage = i / self.number_of_locations
            current_score = int(start_score + 1 + (percentage**scaling) * (max_score - start_score - 2))
            if current_score <= highest_score:
                current_score = highest_score + 1
            highest_score = current_score
            scores += [current_score]

        scores += [max_score]

        # add locations to board, one for every location in the location_table
        all_locations = [
            JigsawLocation(self.player, f"Merge {i} times", 234782000+i, i, board)
            for i in scores
        ]
        board.locations = all_locations
        
        # self.possible_merges is a list, and self.possible_merges[x] is the number of merges you can make with x puzzle pieces
        for loc in board.locations:
            # loc.nmerges is the number of merges for that location. So "Merge 4 times" has nmerges equal to 4
            loc.access_rule = lambda state, count=loc.nmerges: state.has("pcs", self.player, self.pieces_needed_per_merge[count])
            
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
    
    def collect(self, state: "CollectionState", item: "Item") -> bool:
        change = super().collect(state, item)
        if change and "Piece" in item.name:
            pcs: int = int(item.name.split(' ')[0]) if item.name.split(' ')[0].isdigit() else 1
            state.prog_items[item.player]["pcs"] += pcs
        return change

    def remove(self, state: "CollectionState", item: "Item") -> bool:
        change = super().remove(state, item)
        if change and "Piece" in item.name:
            pcs: int = int(item.name.split(' ')[0]) if item.name.split(' ')[0].isdigit() else 1
            state.prog_items[item.player]["pcs"] -= pcs
        return change

    def fill_slot_data(self):
        """
        make slot data, which consists of jigsaw_data, options, and some other variables.
        """
        slot_data = self._get_jigsaw_data()
        jigsaw_options = self.options.as_dict(
            "which_image",
        )
        slot_data = {**slot_data, **jigsaw_options}  # combine the two
        
        slot_data["orientation"] = self.orientation
        slot_data["nx"] = self.nx
        slot_data["ny"] = self.ny
        slot_data["piece_order"] = self.precollected_pieces + self.itempool_pieces
        slot_data["possible_merges"] = self.possible_merges
        slot_data["actual_possible_merges"] = self.actual_possible_merges
        slot_data["ap_world_version"] = self.ap_world_version
        return slot_data
    
    def interpret_slot_data(self, slot_data: Dict[str, Any]):
        self.possible_merges = slot_data["possible_merges"]
        self.pieces_needed_per_merge = [0]
        for i in range(1, self.npieces):
            self.pieces_needed_per_merge.append(next(index for index, value in enumerate(self.possible_merges) if value >= i))

    def write_spoiler(self, spoiler_handle: TextIO) -> None:
        spoiler_handle.write(f"\nSpoiler and info for [Jigsaw] player {self.player}")
        spoiler_handle.write(f"\nPuzzle dimension: {self.nx}×{self.ny}")
        spoiler_handle.write(f"\nPrecollected pieces: {len(self.precollected_pieces)}")
        # spoiler_handle.write(f"\nself.itempool_pieces {self.itempool_pieces} {len(self.itempool_pieces)}")
        # spoiler_handle.write(f"\nself.possible_merges {self.possible_merges} {len(self.possible_merges)}")
        # spoiler_handle.write(f"\nself.actual_possible_merges {self.actual_possible_merges}")
        # spoiler_handle.write(f"\nself.pieces_needed_per_merge {self.pieces_needed_per_merge}\n")