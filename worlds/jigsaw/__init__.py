import math
from typing import Any, Dict, TextIO

from BaseClasses import CollectionState, Entrance, Item, ItemClassification, Region, Tutorial

from worlds.AutoWorld import WebWorld, World

from .Items import JigsawItem, item_table, item_groups, encouragements
from .Locations import JigsawLocation, location_table

from .Options import JigsawOptions, OrientationOfImage, PieceOrder, PieceTypeOrder, jigsaw_option_groups, PlacementOfFillers, Rotations
from .Rules import PuzzleBoard

from worlds.LauncherComponents import (
    Component,
    components,
    Type as component_type,
)


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
    
    option_groups = jigsaw_option_groups
    
    


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
    
    ap_world_version = "0.6.6"

    def _get_jigsaw_data(self):
        return {
            "seed_name": self.multiworld.seed,
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
                if ncv < 1 or nch < 1:
                    continue
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
            self.random.shuffle(pieces_groups[0])
        elif self.options.piece_order_type == PieceTypeOrder.option_four_parts or self.options.piece_order_type == PieceTypeOrder.option_four_parts_non_rotated:
            # Generate a random angle alpha for rotation
            alpha = 0
            if self.options.piece_order_type == PieceTypeOrder.option_four_parts: 
                alpha = self.random.uniform(0, 2 * math.pi)
            cos_alpha = math.cos(alpha)
            sin_alpha = math.sin(alpha)

            # Function to determine the rotated quadrant of a piece
            def get_rotated_quadrant(x, y):
                # Rotate the coordinates
                x_rot = cos_alpha * x - sin_alpha * y
                y_rot = sin_alpha * x + cos_alpha * y

                # Determine the quadrant
                if x_rot >= 0 and y_rot >= 0:
                    return 0  # Top-right
                elif x_rot < 0 and y_rot >= 0:
                    return 1  # Top-left
                elif x_rot < 0 and y_rot < 0:
                    return 2  # Bottom-left
                else:
                    return 3  # Bottom-right

            # Initialize the quadrants
            pieces_groups = [[] for _ in range(4)]

            # Assign each piece to a rotated quadrant
            for y in range(self.ny):
                for x in range(self.nx):
                    piece_number = self.nx * y + x + 1
                    quadrant = get_rotated_quadrant(x - self.nx / 2, y - self.ny / 2)
                    pieces_groups[quadrant].append(piece_number)

            self.random.shuffle(pieces_groups)
            # Shuffle the pieces within each quadrant
            for group in pieces_groups:
                self.random.shuffle(group)
        else:
            corners = [1, self.nx, self.nx * (self.ny - 1) + 1, self.nx * self.ny]
            edges = [i for i in range(2, self.nx)] \
                    + [self.nx * (self.ny - 1) + i for i in range(2, self.nx)] \
                    + [1 + self.nx * i for i in range(1, self.ny - 1)] \
                    + [self.nx + self.nx * i for i in range(1, self.ny - 1)]
            normal = [i for i in range(1, self.npieces + 1) if i not in corners and i not in edges]
            self.random.shuffle(corners)
            self.random.shuffle(edges)
            self.random.shuffle(normal)
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

            # Move a percentage of pieces from each group to the previous group
            for i in range(len(pieces_groups) - 1, 0, -1):
                move_percentage(pieces_groups[i], pieces_groups[i - 1], move_pieces)
            for i in range(len(pieces_groups) - 1):
                move_percentage(pieces_groups[i], pieces_groups[i + 1], move_pieces)
        
        for pieces in pieces_groups:
            self.random.shuffle(pieces)
            
        number_of_checks_out_of_logic = math.ceil(self.options.permillage_of_checks_out_of_logic.value * self.npieces / 1000)
        
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
                        self.random.shuffle(pieces)  # shuffle the remaining pieces
                        
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
                        self.random.shuffle(pieces)  # shuffle the remaining pieces                     
                    
                if p == None:
                    raise RuntimeError("Jigsaw: No piece selected")
                
                # if you have merges left to unlock pieces
                if board.merges_count > len(self.itempool_pieces) + number_of_checks_out_of_logic:
                    self.itempool_pieces.append(p)  # add piece to itempool. The order in this is the order you'll get pcs
                else:
                    self.precollected_pieces.append(p)  # if no merges left, add piece to start_inventory

                board.add_piece(p - 1)
                
                first_piece = False
                
        # compute the number of merges possible when n pieces are collected
                    
        self.possible_merges = [- number_of_checks_out_of_logic]
        self.actual_possible_merges = [0]
        board = PuzzleBoard(self.nx, self.ny)
        
        for c, p in enumerate(self.precollected_pieces):
            board.add_piece(p - 1)
            merges = board.merges_count
            if len(self.itempool_pieces) - c < 10:
                self.possible_merges.append(merges)   
            else:
                self.possible_merges.append(merges - number_of_checks_out_of_logic) 
            self.actual_possible_merges.append(merges)
        for c, p in enumerate(self.itempool_pieces):
            board.add_piece(p - 1)
            merges = board.merges_count
            if len(self.itempool_pieces) - c < 10:
                self.possible_merges.append(merges)   
            else:
                self.possible_merges.append(merges - number_of_checks_out_of_logic)   
            self.actual_possible_merges.append(merges)
        
        self.pieces_needed_per_merge = [0]
        for i in range(1, self.npieces):
            self.pieces_needed_per_merge.append(next(index for index, value in enumerate(self.possible_merges) if value >= i))
        
        
        pieces_left = math.ceil(len(self.itempool_pieces) * (1 + self.options.percentage_of_extra_pieces.value / 100))
        
        max_locs = min(self.npieces - 2,  self.options.maximum_number_of_real_items.value)

        if self.npieces >= 10:
            max_locs -= self.options.fake_pieces.value + self.options.swap_traps.value
            if self.options.rotations != Rotations.option_no_rotation:
                max_locs -= self.options.rotate_traps.value
        
        self.pieces_per_location = max((pieces_left + max_locs - 1) // max_locs, self.options.minimum_number_of_pieces_per_real_item.value)     
        self.number_of_locations = (pieces_left + self.pieces_per_location - 1) // self.pieces_per_location
        self.pool_pieces = [f"{self.pieces_per_location} Puzzle Piece{'s' if self.pieces_per_location > 1 else ''}"] * self.number_of_locations
                                
        pieces_from_start = len(self.precollected_pieces)
        
        while pieces_from_start > 0:
            if pieces_from_start >= 500:
                n = 500
            else:
                n = pieces_from_start
            self.multiworld.push_precollected(self.create_item(f"{n} Puzzle Piece{'s' if n > 1 else ''}"))
            pieces_from_start -= n
        if self.options.fake_pieces.value == 1:
            self.multiworld.push_precollected(self.create_item(f"1 Fake Puzzle Piece"))
            self.fake_pieces_mimic = self.random.choices([i+1 for i in range(self.npieces)], k=2)
        else:
            self.fake_pieces_mimic = []
            
            
    def create_items(self):
        self.multiworld.itempool += [self.create_item(name) for name in self.pool_pieces]
        if self.options.placement_of_fillers == PlacementOfFillers.option_global:
            for i in range(self.filler_items_in_pool):
                self.multiworld.itempool.append(self.create_item(self.filler_encouragements[i]))
        if self.npieces >= 10:
            if self.options.fake_pieces.value == 1:
                self.multiworld.itempool.append(self.create_item("1 Fake Puzzle Piece"))
            if self.options.rotate_traps.value == 1 and self.options.rotations != Rotations.option_no_rotation:
                self.multiworld.itempool.append(self.create_item("Rotate Trap"))
            if self.options.swap_traps.value == 1:
                self.multiworld.itempool.append(self.create_item("Swap Trap"))

    def create_regions(self):        
        # simple menu-board construction
        menu = Region("Menu", self.player, self.multiworld)
        board = Region("Board", self.player, self.multiworld)
        
        max_score = self.npieces - 1
        
        # spread self.number_of_locations piece-items into self.max_score -1 locations
        items = self.number_of_locations 
        if self.npieces >= 10:
            items += self.options.fake_pieces.value + self.options.swap_traps.value
            if self.options.rotations != Rotations.option_no_rotation:
                items += self.options.rotate_traps.value

        locs = max_score - 1  # exclude max_score - 1 which is the win condition        
        
        item_locations = []
        filler_locations = []
        i = 1
        while i < max_score:
            in_a_row = locs
            not_in_a_row = 0
            if locs > items:
                in_a_row = (locs - 1) // (locs - items)
                not_in_a_row = max(1, (locs - items) // (items + 1))
            
            item_locations += [i + j for j in range(in_a_row)]
            filler_locations += [i + in_a_row + j for j in range(not_in_a_row)]
            i += in_a_row + not_in_a_row
            locs -= in_a_row + not_in_a_row
            items -= in_a_row
        
        do_again = True
        while do_again:
            num_pieces = len(self.precollected_pieces)
            
            do_again = False
            for i in range(1, self.npieces - 1):
                
                if i in item_locations:
                    num_pieces += self.pieces_per_location
                if i >= self.possible_merges[min(self.npieces, int(num_pieces))]:
                    do_again = True
                    item_loc_candidates = [loc for loc in item_locations if loc > i]
                    filler_loc_candidates = [loc for loc in filler_locations if loc <= i]
                    if item_loc_candidates and filler_loc_candidates:
                        chosen_item_loc = self.random.choice(item_loc_candidates)
                        item_locations.remove(chosen_item_loc)
                        filler_locations.append(chosen_item_loc)
                        
                        chosen_filler_loc = self.random.choice(filler_loc_candidates)
                        filler_locations.remove(chosen_filler_loc)
                        item_locations.append(chosen_filler_loc)
                    else:
                        raise RuntimeError("Jigsaw: Failed to find location.......")
                    
                    item_locations.sort()
                    filler_locations.sort()
                    
                    num_pieces += self.pieces_per_location  # by swapping you have retro-actively an extra piece
        item_locations.append(self.npieces - 1)  # add the victory location to the item locations

        # add locations to board, one for every location in the location_table
        all_locations = [
            JigsawLocation(self.player, f"Merge {i} times", 234782000+i, i, board)
            for i in item_locations
        ]
        
        ###
        if (self.options.placement_of_fillers == PlacementOfFillers.option_local_only and self.options.enable_forced_local_filler_items.value) or \
            self.options.placement_of_fillers == PlacementOfFillers.option_global:
            all_locations += [
                JigsawLocation(self.player, f"Merge {i} times", 234782000+i, i, board)
                for i in filler_locations
            ]
            # Generate a list of filler_locations random samples from the list encouragements
            self.filler_encouragements = self.random.choices(encouragements, k=len(filler_locations))
                
        board.locations = all_locations

        # self.possible_merges is a list, and self.possible_merges[x] is the number of merges you can make with x puzzle pieces
        for loc in board.locations:
            # loc.nmerges is the number of merges for that location. So "Merge 4 times" has nmerges equal to 4
            loc.access_rule = lambda state, count=loc.nmerges: state.has("pcs", self.player, self.pieces_needed_per_merge[count])
        
        ###
        if self.options.placement_of_fillers == PlacementOfFillers.option_local_only and self.options.enable_forced_local_filler_items.value:
            for i, loc in enumerate(filler_locations):
                self.multiworld.get_location(f"Merge {loc} times", self.player).place_locked_item(self.create_item(self.filler_encouragements[i]))
        ###
        if self.options.placement_of_fillers == PlacementOfFillers.option_global:
            self.filler_items_in_pool = int(self.options.percentage_of_fillers_globally.value / 100 * len(filler_locations))
            for i, loc in enumerate(filler_locations[int(self.filler_items_in_pool):]):
                self.multiworld.get_location(f"Merge {loc} times", self.player).place_locked_item(self.create_item(self.filler_encouragements[i]))

        
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
        return self.random.choice(encouragements)

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
            "rotations",
            "enable_clues",
            "total_size_of_image",
        )
        slot_data = {**slot_data, **jigsaw_options}  # combine the two
        
        slot_data["orientation"] = self.orientation
        slot_data["nx"] = self.nx
        slot_data["ny"] = self.ny
        slot_data["piece_order"] = self.precollected_pieces + self.itempool_pieces
        slot_data["possible_merges"] = self.possible_merges
        slot_data["actual_possible_merges"] = self.actual_possible_merges
        slot_data["fake_pieces"] = self.options.fake_pieces.value
        slot_data["ap_world_version"] = self.ap_world_version
        slot_data["fake_pieces_mimic"] = self.fake_pieces_mimic
        return slot_data
    
    def interpret_slot_data(self, slot_data: Dict[str, Any]):
        self.possible_merges = slot_data["possible_merges"]
        self.nx = slot_data["nx"]
        self.ny = slot_data["ny"]
        self.pieces_needed_per_merge = [0]
        for i in range(1, self.nx * self.ny):
            self.pieces_needed_per_merge.append(next(index for index, value in enumerate(self.possible_merges) if value >= i))

    def write_spoiler(self, spoiler_handle: TextIO) -> None:
        spoiler_handle.write(f"\nSpoiler and info for [Jigsaw] player {self.player}")
        spoiler_handle.write(f"\nPuzzle dimension: {self.nx}×{self.ny}")
        spoiler_handle.write(f"\nPrecollected pieces: {len(self.precollected_pieces)}")
        # spoiler_handle.write(f"\nself.itempool_pieces {self.itempool_pieces} {len(self.itempool_pieces)}")
        # spoiler_handle.write(f"\nself.possible_merges {self.possible_merges} {len(self.possible_merges)}")
        # spoiler_handle.write(f"\nself.actual_possible_merges {self.actual_possible_merges}")
        # spoiler_handle.write(f"\nself.pieces_needed_per_merge {self.pieces_needed_per_merge}\n")
        
    def open_page(url):
        import webbrowser
        import re
        # Extract slot, pass, host, and port from the URL
        # URL format: archipelago://slot:pass@host:port
        match = re.match(r"archipelago://([^:]+):([^@]+)@([^:]+):(\d+)", url)
        if not match:
            raise ValueError("Invalid URL format")
        
        slot, password, host, port = match.groups()
        if password == "None":
            webbrowser.open(f"http://jigsaw-ap.netlify.app/?hostport={host}:{port}&name={slot}")
        else:
            webbrowser.open(f"http://jigsaw-ap.netlify.app/?hostport={host}:{port}&name={slot}&password={password}")

    components.append(
        Component(
            "Jigsaw AutoLaunch",
            func=open_page,
            component_type=component_type.HIDDEN,
            supports_uri=True,
            game_name="Jigsaw"
        )
    )