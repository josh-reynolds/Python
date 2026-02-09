"""Play Tony Dowler's 'How to Host a Dungeon'."""
from typing import Tuple
from pygame import Rect, mouse
from engine import screen, run
from pvector import PVector

WIDTH = 1100
HEIGHT = 850
TITLE = "Testing intersection routines"

def segments_intersect(line_1: Tuple[PVector, PVector], line_2: Tuple[PVector, PVector]) -> bool:
    """Test whether two line segments intersect between their endpoints."""
    r = PVector.sub(line_1[1], line_1[0])
    s = PVector.sub(line_2[1], line_2[0])

    n = PVector.sub(line_2[0], line_1[0])

    u_numerator = n.cross(r)
    denominator = r.cross(s)

    if u_numerator == 0 and denominator == 0:
        # collinear case

        # endpoints touch
        if (line_1[0] == line_2[0] or line_1[0] == line_2[1]
            or line_1[1] == line_2[0] or line_1[1] == line_2[1]):
            return True

        # overlapping segments
        # segments overlap if their projection onto the x axis overlap
        # (or y axis if lines are vertical)

        # projection of AB is:
        # [min(A.x, B.x), max(A.x, B.x)]

        if line_1[0].x != line_1[1].x:     # lines are not vertical
            projection_1 = (min(line_1[0].x, line_1[1].x),
                            max(line_1[0].x, line_1[1].x))

            projection_2 = (min(line_2[0].x, line_2[1].x),
                            max(line_2[0].x, line_2[1].x))

        else:
            projection_1 = (min(line_1[0].y, line_1[1].y),
                            max(line_1[0].y, line_1[1].y))

            projection_2 = (min(line_2[0].y, line_2[1].y),
                            max(line_2[0].y, line_2[1].y))

        return projection_1[0] < projection_2[1] and projection_1[1] > projection_2[0]


    if denominator == 0:
        # parallel case
        return False

    u = u_numerator / denominator
    t = n.cross(s) / denominator

    return t >= 0 and t <= 1 and u >= 0 and u <= 1

# TO_DO: special case - line segment entirely inside the rect
def rect_segment_intersects(rect: Rect, segment: Tuple) -> bool:
    """Test whether a line segment intersects a rectangle."""
    top_left = PVector(rect.x, rect.y)
    top_right = PVector(rect.x + rect.w, rect.y)
    bottom_right = PVector(rect.x + rect.w, rect.y + rect.h)
    bottom_left = PVector(rect.x, rect.y + rect.h)

    top = (top_left, top_right)
    right = (top_right, bottom_right)
    bottom = (bottom_right, bottom_left)
    left = (bottom_left, top_left)

    result = False
    for edge in (top, right, bottom, left):
        if segments_intersect(edge, segment):
            result = True

    return result

lines = [(PVector(550, 100), PVector(550, 750)),
         (PVector(100, 425), PVector(1000, 425))]

cursor = Rect(10, 110, 100, 100)

rects = [Rect(540,90,20,20),
         Rect(90,415,20,20),
         Rect(490,365,120,120),
         Rect(990,415,20,20),
         Rect(540,740,20,20),
         Rect(530,200,20,20),
         Rect(540,230,20,20),
         Rect(550,260,20,20),
         Rect(200,405,20,20),
         Rect(230,415,20,20),
         Rect(260,425,20,20),
         Rect(100,100,20,20),
         Rect(1000,100,20,20),
         Rect(100,730,20,20),
         Rect(1000,730,20,20),
         Rect(530,405,20,20),
         Rect(550,405,20,20),
         Rect(530,425,20,20),
         Rect(550,425,20,20),
         ]

for rectangle in rects:
    print(f"\nChecking {rectangle}")
    for line in lines:
        if rect_segment_intersects(rectangle, line):
            print(f"{line} intersects {rectangle}")

def update() -> None:
    """Update the game state once per frame."""
    coordinate = PVector(*mouse.get_pos())
    cursor.x = coordinate.x - cursor.w/2
    cursor.y = coordinate.y - cursor.h/2

    for line in lines:
        if rect_segment_intersects(cursor, line):
            print(f"{line} intersects")

def draw() -> None:
    """Draw the game to the screen once per frame."""
    # BACKGROUND
    screen.draw.rect(0, 0, WIDTH, HEIGHT, (81, 76, 34), 0)

    # CURSOR
    screen.draw.rect(cursor.x, cursor.y, cursor.h, cursor.w, (255,0,0), 1)

    for rect in rects:
        screen.draw.rect(rect.x, rect.y, rect.h, rect.w, (255,0,255), 1)

    for line in lines:
        screen.draw.line((0,0,0), (line[0].x, line[0].y), (line[1].x, line[1].y), 4)

run()
