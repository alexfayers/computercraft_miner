from cc import is_turtle, turtle
from cc import term

move_length = 10

TURTLE_SLOTS = 16

REFUEL_THRESH = 1

FUEL_TYPES = ['coal']

term.clear()

if not is_turtle():
    print('Turtle required!')
    exit()


def find_item(search):
    for slot in range(1, TURTLE_SLOTS + 1):
        info = turtle.getItemDetail(slot)

        if info is not None and search in info['name']:
            return slot
    return False

def refuel_from_inventory():
    for fuel_type in FUEL_TYPES:
        if find_item(fuel_type):

            return True
    return False


def check_fuel():
    level = turtle.getFuelLevel()

    if level <= REFUEL_THRESH:
        # do some error stuff here ?
        pass

    return level

#refuel_from_inventory()

#exit()

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