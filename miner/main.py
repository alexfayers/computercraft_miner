from cc import is_turtle, turtle
from cc import term

move_length = 10

TURTLE_SLOTS = 16

term.clear()

if not is_turtle():
    print('Turtle required!')
    exit()


def findItem():
    for slot in range(1, TURTLE_SLOTS + 1):
        info = turtle.getItemDetail(slot)

        print(info)


def checkFuel():
    level = turtle.getFuelLevel()

    if level <= 0:
        # do some error stuff here ?
        pass

    return level

findItem()

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