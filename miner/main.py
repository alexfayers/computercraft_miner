from cc import is_turtle, turtle
from cc import term

move_length = 10

term.clear()

if not is_turtle():
    print('Turtle required!')
    exit()

for _ in range(move_length):

    if turtle.detect():
        turtle.dig()
    turtle.forward()

    if turtle.detectUp():
        turtle.digUp()
    turtle.up()

    if turtle.detect():
        turtle.dig()
    turtle.forward()

    if turtle.detectDown():
        turtle.digDown()
    turtle.Down()

# turn around
turtle.turnRight()
turtle.turnRight()

for _ in range(move_length):
    turtle.forward()

# turn around again
turtle.turnRight()
turtle.turnRight()