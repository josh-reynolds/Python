

class Actor:
    def __init__(self, coordinate, level):
        self.pos = coordinate
        self.level = level
        self.time = 0
        self.current_image = 0

    def update(self):
        self.time += 1
        if self.time > 25:
            self.time = 0
            if self.current_image == 0:
                self.current_image = 1
            else:
                self.current_image = 0

    def move(self, dx, dy):
        if self.can_move(dx, dy):
            self.pos = (self.pos[0] + dx,
                        self.pos[1] + dy)
