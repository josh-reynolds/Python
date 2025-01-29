
class Action():
    def __init__(self, target):
        pass
    def execute(self):
        pass

class North(Action):
    def __init__(self, target):
        self.name = 'North'
        self.target = target
    def execute(self):
        self.target.move(0,-1)

class South(Action):
    def __init__(self, target):
        self.name = 'South'
        self.target = target
    def execute(self):
        self.target.move(0,1)

class East(Action):
    def __init__(self, target):
        self.name = 'East'
        self.target = target
    def execute(self):
        self.target.move(1,0)

class West(Action):
    def __init__(self, target):
        self.name = 'West'
        self.target = target
    def execute(self):
        self.target.move(-1,0)

class Pass(Action):
    def __init__(self, target):
        self.name = 'Pass'
        self.target = target
    def execute(self):
        pass

class Quit(Action):
    def __init__(self, target):
        self.name = 'Quit'
        self.target = target
    def execute(self):
        self.target.running = False
