"""Testing line segment intersection routines."""
from pygame import Rect, mouse
from engine import screen, run
from pvector import PVector
from intersections import rect_segment_intersects

WIDTH = 1100
HEIGHT = 850
TITLE = "Testing intersection routines"

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
