from engine import screen

def draw_circle(x, y, radius):
    screen.draw.circle(x, y, radius, (0,0,0), 1)
    if radius > 2:
        draw_circle(x + radius/2, y, radius/2)
        draw_circle(x - radius/2, y, radius/2)
        draw_circle(x, y + radius/2, radius/2)
        draw_circle(x, y - radius/2, radius/2)

def cantor(x, y, l):
    if l >= 1:
        screen.draw.line((0,0,0), (x,y), (x+l,y))
        y += 20
        cantor(x, y, l/3)
        cantor(x + l * 2/3, y, l/3)
