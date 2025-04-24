from dataclasses import dataclass

from Options import Choice, PerGameCommonOptions, Range, Toggle, OptionGroup

class NumberOfPieces(Range):
    """
    Approximate number of pieces in the puzzle.
    Note that this game is more difficult than regular jigsaw puzzles, because you don't start with all pieces :)
    Also make sure the pieces fit on your screen if you choose more than 1000.
    """

    display_name = "Number of pieces"
    range_start = 4
    range_end = 2000
    default = 50
    
class MaximumNumberOfRealItems(Range):
    """
    Jigsaw has two types of items: "real items" and forced local filler items.
    All puzzle pieces you want are contained in the "real items" (these items can give multiple pieces at once).
    
    Only the "real items" are shuffled across the multiworld.
    The forced local filler items have no effect on the multiworld and are just to make every merge be a check. 
    They only show everybody how good you're puzzling and give you additional dopamine every time you merge.
    
    Having too many real items may hurt the multiworld: in many cases, it is not fun to have 1000 "1 Puzzle Piece"
    items in the itempool, especially not for other players that may have way less checks or really hard checks.
    For solo games I would recommend to put this to the maximum.
    """
    
    display_name = "Maximum number of real items"
    range_start = 25
    range_end = 2000
    default = 250
    
class MinimumNumberOfPiecesPerRealItem(Range):
    """
    Remember the real items that are shuffled across the multiworld?
    This option determines the minimum number of pieces that you will be given per item.
    Finding "1 Puzzle Piece" items may not be fun, so this option can make it least at 2 pieces per item for example.
    For solo games I would recommend to put this to 1.
    """
    
    display_name = "Minimum number of pieces per real item"
    range_start = 1
    range_end = 100
    default = 1
    
class EnableForcedLocalFillerItems(Toggle):
    """
    This option adds forced local filler items to your game so every merge is a check.
    Disabling these local filler items has no influence on the multiworld at all, since only local checks are removed.
    I see no reason to turn this off, except when a host is adament that you limit the number of checks.
    """
    
    display_name = "Enable forced local filler items"
    default = True

    
class OrientationOfImage(Choice):
    """
    If you're using a custom image, select the orientation here.
    """

    display_name = "Orientation of image"
    option_square = 1
    option_landscape = 2
    option_portrait = 3
    default = 2


class WhichImage(Range):
    """
    Only if you selected the landscape orientation option.
    This option will decide which landscape picture will be set for you. Don't worry, you can change it in the game.
    Every number corresponds to a set image. See the images here: https://jigsaw-ap.netlify.app/images.html
    """
    
    display_name = "Which image"
    range_start = 1
    range_end = 40
    default = "random"
    
class PercentageOfExtraPieces(Range):
    """
    This option allows for there being more pieces in the pool than necessary.
    When you have all your items already, the additional pieces don't do anything anymore.
    0 means there are exactly enough pieces in the pool.
    100 means there are twice as many pieces in the pool than necessary.
    That means you would only need half of your items to finish the game.
    """

    display_name = "Percentage of extra pieces"
    range_start = 0
    range_end = 100
    default = 10
    
class PieceTypeOrder(Choice):
    """
    This option affects the order in which you receive puzzle piece types (corners, edges, normal).
    This is prioritized over the Piece Order option.
    
    four_parts:
    The board will be divided into four (rotated) quadrants.
    You will first get all pieces of one of the first quadrant, then for the second, etc.
    This makes it so that you're basically starting and finishing a section four times in your playthrough.
    This may be nice for big puzzles, it decreases the pressure at the start, while making the ending more interesting.
    """

    display_name = "Piece type order"
    option_random_order = 1
    option_corners_edges_normal = 2
    option_normal_edges_corners = 3
    option_edges_normal_corners = 4
    option_corners_normal_edges = 5
    option_normal_corners_edges = 6
    option_edges_corners_normal = 7
    option_four_parts = 8
    default = 1
    
class StrictnessPieceTypeOrder(Range): 
    """
    This option determines how strictly the above piece type order is followed.
    1 means it is barely followed, 100 means it is followed in the strictest way possible.
    """

    display_name = "Strictness piece type order"
    range_start = 1
    range_end = 100
    default = 100
    
class PieceOrder(Choice):
    """
    This option affects the order in which you receive puzzle pieces.
    random_order: pieces are added in random order with no extra constraints whatsoever
    every_piece_fits: every piece you receive, will be able to merge with another piece
    least_merges_possible: you will receive pieces in an order that gives the least number of possible merges
    """

    display_name = "Piece order"
    option_random_order = 1
    option_every_piece_fits = 3
    option_least_merges_possible = 4
    default = 1
    
class StrictnessPieceOrder(Range): 
    """
    This option determines how strictly the above piece order is followed.
    1 means it is barely followed, 100 means it is followed in the strictest way possible.
    """

    display_name = "Strictness piece order"
    range_start = 1
    range_end = 100
    default = 100
    
class PermillageOfChecksOutOfLogic(Range):
    """
    It might be hard to find the one connection you can make.
    As such, this option will make it so that there are always additional checks not considered by logic.
    This makes it easier to get "all your checks in logic".
    Of course this won't make a difference at the very end when few merges are left.
    
    A "permillage" is 1/10 of a percentage. 1 percent = 10 permillage
    The number of checks out of logic is: [total number of pieces] * [this option] / 1000 rounded up.
    """

    display_name = "Permillage of checks out of logic"
    range_start = 0
    range_end = 100
    default = 5

class Rotations(Choice):
    """
    Something to make it more realistic but also much harder: pieces can be rotated!
    """

    display_name = "Rotations"
    option_no_rotation = 0
    option_per_90_degrees = 90
    option_per_180_degrees = 180
    default = 0
    
class EnableClues(Toggle):
    """
    Enable clues for the jigsaw puzzle, which shows the outline of pieces that can merge.
    If enabled, can be used as many times as you want.
    If disabled, the button is simply not there.
    """

    display_name = "Enable clues"
    default = True
    
class TotalSizeOfImage(Range):
    """
    The percentage of your game that makes up the image and the puzzle. Default should be fine,
    but you can change it if you want to make it smaller or bigger.
    """

    display_name = "Total size of image"
    range_start = 30
    range_end = 100
    default = 85

@dataclass
class JigsawOptions(PerGameCommonOptions):
    number_of_pieces: NumberOfPieces
    rotations: Rotations
    percentage_of_extra_pieces: PercentageOfExtraPieces
    maximum_number_of_real_items: MaximumNumberOfRealItems
    minimum_number_of_pieces_per_real_item: MinimumNumberOfPiecesPerRealItem
    enable_forced_local_filler_items: EnableForcedLocalFillerItems
    permillage_of_checks_out_of_logic: PermillageOfChecksOutOfLogic
    orientation_of_image: OrientationOfImage
    which_image: WhichImage
    piece_order_type: PieceTypeOrder
    strictness_piece_order_type: StrictnessPieceTypeOrder
    piece_order: PieceOrder
    strictness_piece_order: StrictnessPieceOrder
    enable_clues: EnableClues
    total_size_of_image: TotalSizeOfImage
    
jigsaw_option_groups = [
    OptionGroup(
        "Important: gameplay options",
        [
            NumberOfPieces,
            Rotations,
        ],
    ),
    OptionGroup(
        "Important: image", 
        [
            OrientationOfImage,
            WhichImage, 
        ],
    ),
    OptionGroup(
        "Optional: extra pieces, items and checks",
        [
            PercentageOfExtraPieces,
            MaximumNumberOfRealItems,
            MinimumNumberOfPiecesPerRealItem,
            EnableForcedLocalFillerItems,
            PermillageOfChecksOutOfLogic,
        ],
    ),
    OptionGroup(
        "Optional: piece order", 
        [
            PieceTypeOrder,
            StrictnessPieceTypeOrder,
            PieceOrder,
            StrictnessPieceOrder
        ],
    ),
    OptionGroup(
        "Optional: others", 
        [
            EnableClues,
            TotalSizeOfImage,
        ],
    ),
]
