from dataclasses import dataclass

from Options import Choice, PerGameCommonOptions, Range

class NumberOfPieces(Range):
    """
    Approximate number of pieces in the puzzle.
    I'm really hoping to increase the max, but with more pieces it becomes really slow...
    """

    display_name = "Number of pieces"
    range_start = 25
    range_end = 1000
    default = 25
    
class OrientationOfImage(Choice):
    """
    If you're using a custom image, select the orientation here.
    """

    display_name = "Orientation of image"
    option_square = 1
    option_landscape = 2
    option_portrait = 3
    default = 1
    
class PercentageOfExtraPieces(Range):
    """
    This option allows for there being more pieces in the pool than necessary.
    0 means there are exactly enough pieces in the pool.
    100 means there are twice as many pieces in the pool than necessary.
    That means you would only need half of your items to finish the game.
    """

    display_name = "Percentage of extra pieces"
    range_start = 0
    range_end = 100
    default = 10
    
class PieceOrder(Choice):
    """
    This option affects the order in which you receive puzzle pieces.
    random_order: pieces are added in random order with no extra constraints whatsoever
    corners_edges_rest: corners have the highest chance to appear first, then edges, then the other pieces
    """

    display_name = "Piece order"
    option_random_order = 1
    option_corners_edges_rest = 2
    default = 1
    
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
    percentage_of_extra_pieces: PercentageOfExtraPieces
    piece_order: PieceOrder
    number_of_checks_out_of_logic: NumberOfChecksOutOfLogic