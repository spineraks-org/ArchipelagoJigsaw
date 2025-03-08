from dataclasses import dataclass

from Options import Choice, PerGameCommonOptions, Range, Toggle

class NumberOfPieces(Range):
    """
    Approximate number of pieces in the puzzle.
    """

    display_name = "Number of pieces"
    range_start = 25
    range_end = 1000
    default = 25
    
class AllowFillerItems(Toggle):
    """
    If this option is enabled, the pool will contain several Squawks.
    Squawks is the green-feathered parrot that helps Donkey Kong find puzzle pieces, but in this game they're useless.
    If this option is disabled, no filler items will be in the pool and every item will be one or more puzzle pieces.
    """

    display_name = "Allow filler item"
    default = False
    
class PercentageOfMergesThatAreChecks(Range):
    """
    This option affects the number of checks that are in the pool.
    100 means every merge will be a check. So with 500 merges, there will be 500 checks.
    10 means 10% of all merges will result in a check. If you have 500 merges, there will be 50 checks.
    If you have selected fewer checks, items like "5 Puzzle Pieces" will be shuffled into the pool.
    Note that 100% may not be reached if you disable filler items, in that case there will simply be less checks.
    """

    display_name = "Percentage of merges that are checks"
    range_start = 10
    range_end = 100
    default = 100
    
class MaximumNumberOfChecks(Range):
    """
    The pool can be filled with puzzle pieces really quickly. 
    When there are hundred of puzzle pieces in the pool, it really changes the dynamics in multiworlds.
    As such, by default, there are at most 100 checks and items for Jigsaw.
    If you choose a larger puzzle, you will receive multiple pieces at once.
    This setting overrides the previous option.
    """
    
    display_name = "Maximum number of checks"
    range_start = 25
    range_end = 1000
    default = 100
    
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
    *ONLY IF YOU SELECTED THE LANDSCAPE ORIENTATION*
    This option will decide which landscape picture will be set for you. Don't worry, you can change it in the game.
    Every number corresponds to a set image. See the images here: https://jigsaw-ap.netlify.app/images.html
    """
    
    display_name = "Which image"
    range_start = 1
    range_end = 16
    default = "random"
    
class PercentageOfExtraPieces(Range):
    """
    This option allows for there being more pieces in the pool than necessary.
    When you have all your items already, the additional don't do anything anymore.
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
    """

    display_name = "Piece type order"
    option_random_order = 1
    option_corners_edges_normal = 2
    option_normal_edges_corners = 3
    option_edges_normal_corners = 4
    option_corners_normal_edges = 5
    option_normal_corners_edges = 6
    option_edges_corners_normal = 7
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
    
class NumberOfChecksOutOfLogic(Range):
    """
    It might be hard to find the one connection you can make.
    As such, this option will make it so that there are always additional checks not considered by logic.
    This makes it easier to get "all your checks in logic".
    Of course this won't make a difference at the very end when few pieces are left.
    """

    display_name = "Number of checks out of logic"
    range_start = 0
    range_end = 10
    default = 1


@dataclass
class JigsawOptions(PerGameCommonOptions):
    number_of_pieces: NumberOfPieces
    orientation_of_image: OrientationOfImage
    allow_filler_items: AllowFillerItems
    percentage_of_merges_that_are_checks: PercentageOfMergesThatAreChecks
    maximum_number_of_checks: MaximumNumberOfChecks
    which_image: WhichImage
    percentage_of_extra_pieces: PercentageOfExtraPieces
    piece_order_type: PieceTypeOrder
    strictness_piece_order_type: StrictnessPieceTypeOrder
    piece_order: PieceOrder
    strictness_piece_order: StrictnessPieceOrder
    number_of_checks_out_of_logic: NumberOfChecksOutOfLogic