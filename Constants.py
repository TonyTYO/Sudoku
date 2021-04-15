# -------------------------------------------------------------------------------
# Name:        Constants
# Purpose:
#
# Author:      Tony
#
# Created:     22/07/2016
# Copyright:   (c) Tony 2016
# Licence:     <your licence>
# -------------------------------------------------------------------------------
""" Set of constants used in the game """

# Size of grids square size: subsquare sizes
SIZE_DICT = {4: (2, 2), 6: (3, 2), 8: (4, 2), 9: (3, 3), 10: (5, 2), 12: (4, 3)}
# Following not implemented
# {14: (7, 2), 15: (5, 3), 16: (4, 4),20: (5, 4), 25: (5, 5)}

# All digits used
DIGITS = "123456789ABC"

SIZE = 9  # Default number of squares on a side.
MID_ROW = SIZE / 2  # The coordinates of the center (starting) square.
MID_COL = SIZE / 2
CELL_COUNT = SIZE * SIZE  # Number of squares on the board.
WIDTH = 50  # Width of each square/tile
HEIGHT = 50  # Height of each square/tile
MARGIN = 5  # Margin between each cell
INT_CELLS = 3

# Board square colours
NORMAL_COLOUR = (255, 255, 255)

# Playing board
WINDOW_SIZE = [1300, 780]  # Window size
BOARD_WIDTH = 9 * (WIDTH + MARGIN) + MARGIN  # width of playing board
BOARD_HEIGHT = 9 * (HEIGHT + MARGIN) + MARGIN  # height of playing board
BOARD_X = (WINDOW_SIZE[0] - BOARD_WIDTH) / 2  # x-coordinate of scrabble board
BOARD = [BOARD_X, 50, BOARD_WIDTH, BOARD_HEIGHT]  # board rect details

SPLASH_SIZE = [450, 250]

# position and size of buttons
LARGE_BUTTON = 50
SMALL_BUTTON = 40
BUTTON_X = WINDOW_SIZE[0] - MARGIN * 2 - 120 - LARGE_BUTTON
BUTTON_Y = 150
PLAY_BUTTON = [0, 0]
CHECK_BUTTON = [100, 0]
HINT_BUTTON = [0, 90]
RESTART_BUTTON = [100, 90]
SOLVE_BUTTON = [0, 180]
STEP_BUTTON = [100, 180]
LOAD_BUTTON = [0, 300]
SAVE_BUTTON = [100, 300]
SETUP_BUTTON = [0, 390]
CLEAR_BUTTON = [100, 390]
PRINT_BUTTON = [50, 480]
QUIT_BUTTON = [50, 600]

# position of racks and tiles in racks
RACK_POS = [MARGIN * 2, WINDOW_SIZE[0] - MARGIN * 2 - 315]  # x-position of racks
RACK_Y = WINDOW_SIZE[1] - 150
RACK_XTILE = [MARGIN * 2 + 20, WINDOW_SIZE[0] - MARGIN * 2 - 315 + 20]
RACK_YTILE = BOARD[1]

TILE_WIDTH = 50
TILE_HEIGHT = 50

SQUARE_WIDTH = 10 * (WIDTH + MARGIN) + MARGIN  # width of square
SQUARE_HEIGHT = 10 * (HEIGHT + MARGIN) + MARGIN  # height of square
SQUARE_X = (WINDOW_SIZE[0] - SQUARE_WIDTH) / 2  # x-coordinate
SQUARE_Y = (WINDOW_SIZE[1] - SQUARE_HEIGHT) / 2  # y-coordinate
INSTR_RECT = [SQUARE_X - 10, SQUARE_Y + SQUARE_HEIGHT + 40, SQUARE_WIDTH + 20, 60]

FUNC_MSGS = ["Naked Singles\nOnly one possibility in the cell",
             "Hidden Singles\nOnly one possible but hidden",
             "Pointing Pair\nThis adjusts possibles but does not set any numbers",
             "Block-Block\nThis adjusts possibles but does not set any numbers",
             "Naked Subsets\nThis adjusts possibles but does not set any numbers",
             "Hidden Subsets\nThis adjusts possibles but does not set any numbers",
             "Backtracking\nThis tries all possible values in turn"]

#  SVG for tile

SVG_DATA_1 = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg width="50" height="50" id="smile" version="1.1">
    <rect x="0" y="0" rx="5" ry="5" width="50" height="50"
     style="fill:white;stroke:white;stroke-width:1;fill-opacity:0; stroke-opacity:0" />
    <text x="25" y="32" font-family="Arial, sans-serif" font-size="28pt" font-weight="bold" 
     text-anchor="middle" dominant-baseline="middle" fill="{col}">{one}</text>
</svg>
"""
#  SVG for hints

SVG_HINT_1 = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg width="50" height="50" viewBox="0 0 50 50" id="hint" version="1.1">"""

SVG_HINT_2 = """<line x1="{start_x}" x2="{end_x}" y1="{start_y}" y2="{end_y}" stroke="gray" stroke-width="1"/>"""

SVG_HINT_3 = """<text x="{x}" y="{y}" font-family="Arial, sans-serif" font-size="12pt" 
text-anchor="middle" dominant-baseline="middle" fill="black">{num}</text>"""

# SVG for printing grid

SVG_PRINT_1 = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg
   width="{box}"
   height="{box}"
   viewBox="0 0 {box} {box}"
   id="svg2"
   version="1.1"
>
"""

SVG_PRINT_2 = """   
<!-- Set up grid -->
<rect width="{box}" height="{box}" fill="white"/>

<g id="layer1"
    >
    <g id="g4748"
        >
        <rect
             style="opacity:1;fill:white;fill-opacity:1;stroke:#0f0404;stroke-width:3;stroke-linejoin:round;stroke-miterlimit:4;stroke-dasharray:none;stroke-opacity:1"
             id="rect3924"
             width="{rect}"
             height="{rect}"
             x="{margin}"
             y="{margin}" />
"""

SVG_PRINT_3 = """
        <path
             style="color:#000000;clip-rule:nonzero;display:inline;overflow:visible;visibility:visible;opacity:1;isolation:auto;mix-blend-mode:normal;color-interpolation:sRGB;color-interpolation-filters:linearRGB;solid-color:#000000;solid-opacity:1;fill:none;fill-opacity:1;fill-rule:evenodd;stroke:#1a0707;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:4;stroke-dasharray:none;stroke-dashoffset:0;stroke-opacity:1;color-rendering:auto;image-rendering:auto;shape-rendering:auto;text-rendering:auto;enable-background:accumulate"
             d="m {start_x},{start_y} l {end_x},{end_y}"
             id="path4738" />
             """

SVG_PRINT_4 = """
        <path
             style="color:#000000;clip-rule:nonzero;display:inline;overflow:visible;visibility:visible;opacity:1;isolation:auto;mix-blend-mode:normal;color-interpolation:sRGB;color-interpolation-filters:linearRGB;solid-color:#000000;solid-opacity:1;fill:none;fill-opacity:1;fill-rule:evenodd;stroke:#1a0707;stroke-width:1;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:4;stroke-dasharray:none;stroke-dashoffset:0;stroke-opacity:1;color-rendering:auto;image-rendering:auto;shape-rendering:auto;text-rendering:auto;enable-background:accumulate"
             d="m {start_x},{start_y} l {end_x},{end_y}"
             id="path4754" />
             """

SVG_PRINT_5 = """
    </g>
</g>

<!-- Numbers in squares go here as <text> elements
     Cannot use <svg> subelements in QT (uses SVG Tiny)
 -->
 """

SVG_PRINT_6 = """
<text x="{x}" y="{y}" font-family="Arial, sans-serif" 
                      font-size="{font_size}pt" 
                      text-anchor="middle" 
                      fill="{col}">{num}</text>"""
