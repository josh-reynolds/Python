"""Draw a Traveller-style star map."""

from random import random
from typing import List, Dict, Tuple
from PIL import Image, ImageDraw, ImageFont
from src.star_system import Hex, StarSystem

SIZE = 40
COLUMNS = 8
ROWS = 10

# fiddling with numbers, may be some floating point truncation
# to consider in translating to pixel coordinates

# the math says:
# r = hexagon radius

# a = hex center to side distance
#   = r * cos(30)
#   = 0.866 * r

# v_sep = 2 * a
#       = 2 * 0.866 * r
#       = 1.732 * r

# offset column adjust = a
#
# h_sep = 2 * a * cos(30)
#       = 1.732 * a
#       = 1.732 * 0.866 * r
#       = 1.4999 * r

# numbers below established through experimentation,
# and look good at this size (SIZE=40, 600x800 canvas)
# may be fragile if radius (i.e. SIZE) changes
V_BORD_EVEN = int(1.2 * SIZE) + 30
V_BORD_ODD = int(2.1 * SIZE) + 30
V_SEP = int(1.75 * SIZE)
H_BORDER = int(1.2 * SIZE) + 40
H_SEP = int(1.5 * SIZE)

DOT_RADIUS = SIZE / 4.5

# COLORS
BACKGROUND = (0,0,0)
HEX_LINES = (50,79,53)
COORD = (100,100,100)
WORLD = (27,66,170)
GAS_GIANT = (190,190,190)
WORLD_NAME = (200,200,200)
STARPORT = (200,200,200)
TITLE = (255,255,255)

# This is not portable. Either see what default font looks like,
# or package a font with this application.
FONT_NAME = "/nix/store/q74idm55v5km2pp9yh5qhzc4cw639kp4-cantarell-fonts-0.303.1" +\
           "/share/fonts/cantarell/Cantarell-VF.otf"
font_reg = ImageFont.truetype(FONT_NAME, 16)
font_sm = ImageFont.truetype(FONT_NAME, 12)

def draw_hexes_on(surface, systems: Dict[Tuple, Hex]) -> None:
    """Draw a grid of hexes on the supplied surface."""
    # we will need to have a lookup by coordinate, need
    # a dictionary by trav_coord I think
    #
    # or we could convert coords here into Coordinate,
    # and continue to use that as dict key

    for j in range(COLUMNS):
        for i in range(ROWS):
            if j % 2 == 0:
                v_bord = V_BORD_EVEN
            else:
                v_bord = V_BORD_ODD

            center_x = H_BORDER + H_SEP * j
            center_y = v_bord + V_SEP * i

            hex_content = systems.get((j+1,i+1), "empty")

            draw_hex(surface, center_x, center_y, j+1, i+1)

            if isinstance(hex_content, StarSystem):
                draw_system(surface, center_x, center_y, j+1, i+1, hex_content)

def draw_system(surface, center_x: int, center_y: int,
                column: int, row: int, system: StarSystem) -> None:
    """Draw StarSystem graphics on the supplied surface."""
    # WORLD
    surface.ellipse([center_x - DOT_RADIUS,
                     center_y - DOT_RADIUS,
                     center_x + DOT_RADIUS,
                     center_y + DOT_RADIUS],
                    fill=WORLD)

    # GAS GIANT
    surface.ellipse([center_x - DOT_RADIUS/3 + 15,
                     center_y - DOT_RADIUS/3 - 12,
                     center_x + DOT_RADIUS/3 + 15,
                     center_y + DOT_RADIUS/3 - 12],
                    fill=GAS_GIANT)

    # WORLD NAME
    surface.text((center_x, center_y + 23),
                 system.name,
                 font=font_sm,
                 anchor="mm",
                 fill=WORLD_NAME)

    # STARPORT
    surface.text((center_x, center_y - 12),
                 system.starport,
                 font=font_sm,
                 anchor="mb",
                 fill=STARPORT)

def draw_hex(surface, center_x: int, center_y: int,
             column: int, row: int) -> None:
    """Draw an empty Traveller map hex on the supplied surface."""
    surface.regular_polygon((center_x, center_y, SIZE),
                            6,
                            outline=HEX_LINES)

    surface.text((center_x, center_y - 23),
                 f"{column:02d}{row:02d}",
                 font=font_sm,
                 anchor="mb",
                 fill=COORD)

def draw_map(systems: List[Hex]) -> None:
    """Create a map image and write to a file."""
    sys_dict = {}
    for system in systems:
        sys_dict[system.coordinate.trav_coord[0]] = system
    print(sys_dict)
    _ = input("Press ENTER key to continue.")
    image = Image.new(mode="RGB", size=(600,800), color=BACKGROUND)
    draw = ImageDraw.Draw(image)
    draw_hexes_on(draw, sys_dict)
    draw.text((H_BORDER/2,10), "Subsector Map", font=font_reg, fill=TITLE)
    image.save("subsector_map.png")
