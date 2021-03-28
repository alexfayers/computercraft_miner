from cc import is_turtle, turtle
from cc import term
from cc import gps

move_length = 10

term.clear()

if not is_turtle():
    print('Turtle required!')
    exit()

for _ in range(move_length):
    location = gps.locate()
    if location:
        print(locationn)

    if turtle.detect():
        turtle.dig()
    if turtle.detectUp():
        turtle.digUp()

    turtle.forward()

# turn around
turtle.turnRight()
turtle.turnRight()

for _ in range(move_length):
    turtle.forward()

# turn around again
turtle.turnRight()
turtle.turnRight()