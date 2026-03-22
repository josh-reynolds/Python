"""Contains size, color and string constants."""

WIDTH = 1100
HEIGHT = 850
TITLE = "How to Host a Dungeon"

GROUND_LEVEL = HEIGHT // 5
STRATA_HEIGHT = (HEIGHT - GROUND_LEVEL) // 6
COLUMN_WIDTH = WIDTH // 12
BEAD = 30
FINGER = HEIGHT // 5
MARGIN = BEAD

ROOM_SPACING = 50

SKY = (36, 87, 192)
GROUND = (81, 76, 34)
MITHRIL = (255,255,255)
GOLD = (255, 255, 0)
BORDER = (0, 0, 0)
CAVERN = (0, 0, 0)
WATER = (0, 0, 255)

EVENT = (128,128,128)
TREASURE = (255,255,0)

# may want to have foreground/background colors
# for each 'team' so we can show claimed territory
DWARF_TERRITORY = (100, 80, 255)
DWARF = (255,0,255)
BEASTS = (255,0,0)
WYRM = (0,255,0)

SHOW_LABELS = False
