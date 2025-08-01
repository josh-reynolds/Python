"""Chapter 8 - Using Matrices for Computer Graphics."""
from math import sin, cos, pi
import pygame
from engine import run, remap
from screen_matrix import line, push_matrix, pop_matrix, translate, sm, polygon
# pylint: disable=C0103, C0200

WIDTH = 600
HEIGHT = 600
TITLE = "Matrices"

def add_matrices(a,b):
    """Add two 2x2 matrices together."""
    C = [[a[0][0] + b[0][0], a[0][1] + b[0][1]],
         [a[1][0] + b[1][0], a[1][1] + b[1][1]]]
    return C

def mult_matrices(a,b):
    """Multiply two matrices together."""
    m = len(a)
    n = len(b[0])
    new_matrix = []
    for i in range(m):
        row = []
        for j in range(n):
            sum1 = 0
            for k in range(len(b)):
                sum1 += a[i][k] * b[k][j]
            row.append(sum1)
        new_matrix.append(row)
    return new_matrix

def grid():
    """Draw a grid for graphing."""
    sm.color = (0,255,255)
    for i in range(xmin,xmax+1):
        line(i*xscl, ymin*yscl, i*xscl, ymax*yscl)
    for i in range(ymin,ymax+1):
        line(xmin*xscl, i*yscl, xmax*xscl, i*yscl)

    sm.color = (0,0,0)
    line(0, ymin*yscl, 0, ymax*yscl)
    line(xmin*xscl, 0, xmax*xscl, 0)

def graph_points(point_list, edges, color=(0,0,0), width=1):
    """Graphs the points in a list using edges."""
    sm.color = color
    for e in edges:
        line(point_list[e[0]][0] * xscl, point_list[e[0]][1] * yscl,
             point_list[e[1]][0] * xscl, point_list[e[1]][1] * yscl,
             line_weight=width)

def transpose(a):
    """Transpose matrix a."""
    output = []
    m = len(a)
    n = len(a[0])
    for i in range(n):
        output.append([])
        for j in range(m):
            output[i].append(a[j][i])
    return output

def rottilt(rot,tilt):
    """Return the matrices for rotating & tilting a number of degrees."""
    rotmatrix_Y = [[cos(rot), 0.0, sin(rot)],
                   [0.0, 1.0, 0.0],
                   [-sin(rot), 0.0, cos(rot)]]
    rotmatrix_X = [[1.0, 0.0, 0.0],
                   [0.0, cos(tilt), sin(tilt)],
                   [0.0, -sin(tilt), cos(tilt)]]
    return mult_matrices(rotmatrix_Y, rotmatrix_X)

def update():
    """Update the app state once per frame."""

def draw():
    """Draw to the window once per frame."""
    push_matrix()
    translate(WIDTH/2, HEIGHT/2)
    grid()
    mouse_x, mouse_y = pygame.mouse.get_pos()
    rot = remap(mouse_x, 0, WIDTH, 0, pi*2)
    tilt = remap(mouse_y, 0, HEIGHT, 0, pi*2)
    new_matrix = transpose(mult_matrices(rottilt(rot,tilt),
                                         transpose(fmatrix)))
    graph_points(new_matrix, edges, color=(255,0,0), width=3)
    pop_matrix()


xmin = -10
xmax = 10

ymin = -10
ymax = 10

rangex = xmax - xmin
rangey = ymax - ymin

xscl = WIDTH/rangex
yscl = -HEIGHT/rangey

fmatrix = [[0,0,0],[1,0,0],[1,2,0],[2,2,0],[2,3,0],[1,3,0],[1,4,0],[3,4,0],[3,5,0],[0,5,0],
           [0,0,1],[1,0,1],[1,2,1],[2,2,1],[2,3,1],[1,3,1],[1,4,1],[3,4,1],[3,5,1],[0,5,1]]
edges = [[0,1],[1,2],[2,3],[3,4],[4,5],[5,6],[6,7],
         [7,8],[8,9],[9,0],
         [10,11],[11,12],[12,13],[13,14],[14,15],[15,16],[16,17],
         [17,18],[18,19],[19,10],
         [0,10],[1,11],[2,12],[3,13],[4,14],[5,15],[6,16],
         [7,17],[8,18],[9,19]]

run()
