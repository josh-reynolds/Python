from random import randint, random, gauss, uniform

class Walker:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def display(self, surface):
        surface.draw.circle(self.x, self.y, 10, (0,0,0))

    def step(self):
        stepsize = 2 * montecarlo()
        self.x += uniform(-stepsize, stepsize)
        self.y += uniform(-stepsize, stepsize)

# ----------------------------------------------------
def montecarlo():
    while True:
        r1 = random()
        r2 = random()
        if r2 < (r1 ** 2):
            return r1
