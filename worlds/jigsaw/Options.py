from dataclasses import dataclass

from Options import PerGameCommonOptions, Range

class NumberOfPieces(Range):
    """
    Approximate number of pieces in the puzzle.
    """

    display_name = "Number of pieces"
    range_start = 25
    range_end = 1000
    default = 25
    
class WidthOfImage(Range):
    """
    If you're using a custom image, this is the width (in pixels) of your image.
    Input this correctly to get nice square-like puzzle pieces.
    The default value is the width of the default image used in the game.
    """

    display_name = "Width of image"
    range_start = 1
    range_end = 100000
    default = 2034
    
class HeightOfImage(Range):
    """
    If you're using a custom image, this is the height (in pixels) of your image.
    Input this correctly to get nice square-like puzzle pieces.
    The default value is the height of the default image used in the game.
    """

    display_name = "Height of image"
    range_start = 1
    range_end = 100000
    default = 2112

@dataclass
class JigsawOptions(PerGameCommonOptions):
    number_of_pieces: NumberOfPieces
    width_of_image: WidthOfImage
    height_of_image: HeightOfImage