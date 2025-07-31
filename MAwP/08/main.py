"""Chapter 8 - Using Matrices for Computer Graphics."""
from engine import run
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

def graph_points(matrix, color, width):
    """Draw line segments between consecutive points."""
    points = []
    for pt in matrix:
        points.append((pt[0]*xscl,pt[1]*yscl))
    polygon(points, color, width)

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

def update():
    """Update the app state once per frame."""

def draw():
    """Draw to the window once per frame."""
    push_matrix()
    translate(WIDTH/2, HEIGHT/2)
    grid()
    graph_points(fmatrix, (0,0,255), 2)
    graph_points(rotated_matrix, (255,0,0), 2)
    graph_points(f_a, (0,255,0), 2)
    graph_points(f_b, (0,255,255), 2)
    graph_points(f_c, (255,0,255), 2)
    pop_matrix()

xmin = -10
xmax = 10

ymin = -10
ymax = 10

rangex = xmax - xmin
rangey = ymax - ymin

xscl = WIDTH/rangex
yscl = -HEIGHT/rangey

fmatrix = [[0,0],[1,0],[1,2],[2,2],[2,3],[1,3],[1,4],[3,4],[3,5],[0,5]]
transformation_matrix = [[0,-1],[1,0]]
rotated_matrix = transpose(mult_matrices(transformation_matrix,
                                         transpose(fmatrix)))

transform_a = [[1,0],[0,-1]]
transform_b = [[0,-1],[-1,0]]
transform_c = [[-1,1],[1,1]]

f_a = transpose(mult_matrices(transform_a, transpose(fmatrix)))
f_b = transpose(mult_matrices(transform_b, transpose(fmatrix)))
f_c = transpose(mult_matrices(transform_c, transpose(fmatrix)))

print(fmatrix)
print(transpose(fmatrix))

run()
