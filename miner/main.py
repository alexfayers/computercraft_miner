from cc import is_turtle, turtle
from cc import term
from cc import gps

term.clear()

if not is_turtle():
    print('Turtle required!')
    exit()

for _ in range(4):
    x, y, z = gps.locate()

    print(x, y, z)

    if turtle.detect():
        turtle.dig()
    if turtle.detectUp():
        turtle.digUp()

    turtle.forward()
