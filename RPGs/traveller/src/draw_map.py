"""Draw a Traveller-style star map.

draw_hexes_on() - draw a grid of hexes on the supplied surface.

draw_system() - draw StarSystem graphics on the supplied surface.

draw_hex() - draw an empty Traveller map hex on the supplied surface.

draw_map() - create a map image and write to a file.
"""
from typing import List, Dict, Tuple
from PIL import Image, ImageDraw, ImageFont
from src.star_system import Hex, StarSystem
from src.utilities import BOLD_GREEN, END_FORMAT, get_next_file

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

COLORS: Dict[str, Tuple[int,int,int]] = {}

# This is not portable. Either see what default font looks like,
# or package a font with this application.
FONT_NAME = "/nix/store/q74idm55v5km2pp9yh5qhzc4cw639kp4-cantarell-fonts-0.303.1" +\
           "/share/fonts/cantarell/Cantarell-VF.otf"
font_reg = ImageFont.truetype(FONT_NAME, 16)
font_sm = ImageFont.truetype(FONT_NAME, 12)

def draw_hexes_on(surface, systems: Dict[Tuple[int,int], Hex]) -> None:
    """Draw a grid of hexes on the supplied surface."""
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
                draw_system(surface, center_x, center_y, hex_content)

def draw_system(surface, center_x: int, center_y: int, system: StarSystem) -> None:
    """Draw StarSystem graphics on the supplied surface."""
    # WORLD
    if system.size > 0:
        if system.hydrographics > 0:
            fill_color = COLORS["WET_WORLD"]
        else:
            fill_color = COLORS["DRY_WORLD"]
        surface.ellipse([center_x - DOT_RADIUS,
                         center_y - DOT_RADIUS,
                         center_x + DOT_RADIUS,
                         center_y + DOT_RADIUS],
                        fill=fill_color)
    else:
        x_offsets = [-7, 6, -3, 6, 0, -9]
        y_offsets = [-7, 5, 2, -4, -8, 0]
        half_widths = [1, 3, 2, 1, 1, 2]
        half_heights = [1, 2, 2, 2, 3, 1]

        for j in range(6):
            x_offset = x_offsets[j]
            y_offset = y_offsets[j]
            half_width = half_widths[j]
            half_height = half_heights[j]

            surface.ellipse([center_x - x_offset - half_width,
                             center_y - y_offset - half_height,
                             center_x - x_offset + half_width,
                             center_y - y_offset + half_height],
                            fill=COLORS["DRY_WORLD"])

    # GAS GIANT
    if system.gas_giant:
        surface.ellipse([center_x - DOT_RADIUS/3 + 15,
                         center_y - DOT_RADIUS/3 - 12,
                         center_x + DOT_RADIUS/3 + 15,
                         center_y + DOT_RADIUS/3 - 12],
                        fill=COLORS["GAS_GIANT"])

    # WORLD NAME
    if system.population > 8:
        name = system.name.upper()
    else:
        name = system.name
    surface.text((center_x, center_y + 23),
                 name,
                 font=font_sm,
                 anchor="mm",
                 fill=COLORS["WORLD_NAME"])

    # STARPORT
    surface.text((center_x, center_y - 12),
                 system.starport,
                 font=font_sm,
                 anchor="mb",
                 fill=COLORS["STARPORT"])

def draw_hex(surface, center_x: int, center_y: int,
             column: int, row: int) -> None:
    """Draw an empty Traveller map hex on the supplied surface."""
    surface.regular_polygon((center_x, center_y, SIZE),
                            6,
                            outline=COLORS["HEX_LINES"])

    surface.text((center_x, center_y - 23),
                 f"{column:02d}{row:02d}",
                 font=font_sm,
                 anchor="mb",
                 fill=COLORS["COORD"])

def draw_map(systems: List[Hex], subsector_name: str, print_friendly: bool=False) -> None:
    """Create a map image and write to a file."""
    if print_friendly:
        COLORS["BACKGROUND"] = (225,225,225)
        COLORS["HEX_LINES"] = (75,75,75)
        COLORS["COORD"] = (75,75,75)
        COLORS["WET_WORLD"] = (60,60,60)
        COLORS["DRY_WORLD"] = (175,175,175)
        COLORS["GAS_GIANT"] = (60,60,60)
        COLORS["WORLD_NAME"] = (0,0,0)
        COLORS["STARPORT"] = (0,0,0)
        COLORS["TITLE"] = (0,0,0)
    else:
        COLORS["BACKGROUND"] = (0,0,0)
        COLORS["HEX_LINES"] = (50,79,53)
        COLORS["COORD"] = (100,100,100)
        COLORS["WET_WORLD"] = (27,66,170)
        COLORS["DRY_WORLD"] = (80,80,80)
        COLORS["GAS_GIANT"] = (190,190,190)
        COLORS["WORLD_NAME"] = (200,200,200)
        COLORS["STARPORT"] = (200,200,200)
        COLORS["TITLE"] = (255,255,255)

    sys_dict = {}
    # TO_DO: dict slice?
    for system in systems:
        sys_dict[system.coordinate.trav_coord[0]] = system
    image = Image.new(mode="RGB", size=(600,800), color=COLORS["BACKGROUND"])

    draw = ImageDraw.Draw(image)
    draw_hexes_on(draw, sys_dict)
    draw.text((H_BORDER/2,10), f"{subsector_name} Subsector", font=font_reg, fill=COLORS["TITLE"])

    no_whitespace = "".join(subsector_name.lower().split())
    filename = get_next_file(no_whitespace, "png")
    image.save("./saves/" + filename)
    print(f"{BOLD_GREEN}Saved to {filename}.{END_FORMAT}")
