from dataclasses import dataclass

from Options import Choice, PerGameCommonOptions, Range

class NumberOfPieces(Range):
    """
    Approximate number of pieces in the puzzle.
    I'm really hoping to increase the max, but with more pieces it becomes really slow...
    """

    display_name = "Number of pieces"
    range_start = 25
    range_end = 250
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

@dataclass
class JigsawOptions(PerGameCommonOptions):
    number_of_pieces: NumberOfPieces
    orientation_of_image: OrientationOfImage