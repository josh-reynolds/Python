import math
from random import random
from pvector import PVector
from screen_matrix import push_matrix, pop_matrix, translate, circle, line
from engine import remap, screen, lerp

class Neuron:
    def __init__(self, x, y, id_):
        self.location = PVector(x,y)
        self.connections = []
        self.sum = 0
        self.id = id_
        self.color = (0,255,0)

    def draw(self):
        for c in self.connections:
            c.draw()
        circle(self.location.x, self.location.y, 16, self.color, 0)
        circle(self.location.x, self.location.y, 16, (0,0,0), 1)

    def update(self):
        for c in self.connections:
            c.update()

    def add_connection(self, connection):
        self.connections.append(connection)

    def feed_forward(self, value):
        self.sum += value
        if self.sum > 1:
            self.fire()
            self.color = (255,0,0)
        else:
            self.color = (0,255,0)

    def fire(self):
        for c in self.connections:
            c.feed_forward(self.sum)
        self.sum = 0

class Network:
    def __init__(self, x, y):
        self.location = PVector(x,y)
        self.neurons = []

    def add_neuron(self, neuron):
        self.neurons.append(neuron)

    def connect(self, a, b):
        a.add_connection(Connection(a, b, random()))

    def draw(self):
        push_matrix()
        translate(self.location.x, self.location.y)
        for n in self.neurons:
            n.draw()
        pop_matrix()

    def feed_forward(self, value):
        start = self.neurons[0]
        start.feed_forward(value)

    def update(self):
        for n in self.neurons:
            n.update()

class Connection:
    def __init__(self, from_, to_, weight):
        self.weight = weight
        self.a = from_
        self.b = to_
        self.sending = False
        self.sender = from_.location.copy()
        self.output = 0

    def draw(self):
        line_weight = math.floor(remap(self.weight, 0, 1, 1, 6))
        line(self.a.location.x, self.a.location.y, self.b.location.x, self.b.location.y, line_weight)
        if self.sending:
            circle(self.sender.x, self.sender.y, 8, (0,0,0), 0)

    def update(self):
        if self.sending:
            self.sender.x = lerp(self.sender.x, self.b.location.x, 0.1)
            self.sender.y = lerp(self.sender.y, self.b.location.y, 0.1)

            d = PVector.dist(self.sender, self.b.location)

            if d < 1:
                self.b.feed_forward(self.output)
                self.sending = False

    def feed_forward(self, value):
        self.output = value * self.weight
        self.sender = self.a.location.copy()
        self.sending = True

class NeuralNetwork:
    def __init__(self, max_width, max_height):
        self.max_width = max_width
        self.max_height = max_height
        self.count = 0

        self.n = Network(self.max_width//2, self.max_height//2)

        self.a = Neuron(-230,0, 'a')
        self.b = Neuron(0,100, 'b')
        self.c = Neuron(0,-100, 'c')
        self.d = Neuron(0,0, 'd')
        self.e = Neuron(200,0, 'e')

        self.n.add_neuron(self.a)
        self.n.add_neuron(self.b)
        self.n.add_neuron(self.c)
        self.n.add_neuron(self.d)
        self.n.add_neuron(self.e)

        self.n.connect(self.a,self.b)
        self.n.connect(self.a,self.c)
        self.n.connect(self.a,self.d)
        self.n.connect(self.b,self.e)
        self.n.connect(self.c,self.e)
        self.n.connect(self.d,self.e)

    def update(self):
        self.n.update()
        self.count += 1
        if self.count % 30 == 0:
            self.n.feed_forward(random())

    def draw(self):
        self.n.draw()
        screen.draw.text(str(self.count), pos=(self.max_width-50,20))
