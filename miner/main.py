from cc import is_turtle, turtle
from cc import term

MOVE_DISTANCE = 10
REFUEL_THRESH = 10
LIGHT_SEPARATION = 15

FUEL_TYPES = ["lava", "blaze", "coal", "wood"]
LIGHTING_TYPES = ["torch"]

# Const type things
TURTLE_SLOTS = 16

term.clear()

if not is_turtle():
    print("Turtle required!")
    exit()


def turn_around():
    turtle.turnRight()
    turtle.turnRight()


def find_item(search):
    for slot in range(1, TURTLE_SLOTS + 1):
        info = turtle.getItemDetail(slot)

        if info is not None and search in info["name"]:
            return slot
    return False


def place_light_from_inventory():  # place a light behind us
    for lighting_type in LIGHTING_TYPES:
        light_slot = find_item(lighting_type)
        if light_slot:
            prevSlot = turtle.getSelectedSlot()
            turtle.select(light_slot)

            turn_around()
            turtle.place()
            turn_around()

            turtle.select(prevSlot)

            print("Light placed behind")

            return True
    return False


def refuel_from_inventory():
    for fuel_type in FUEL_TYPES:
        fuel_slot = find_item(fuel_type)
        if fuel_slot:
            prevSlot = turtle.getSelectedSlot()
            turtle.select(fuel_slot)

            while turtle.getFuelLevel() <= REFUEL_THRESH:
                print("Refueling...")
                turtle.refuel(1)

            turtle.select(prevSlot)
            print("Refueled")

            return True
    return False


def check_fuel():
    level = turtle.getFuelLevel()

    if level <= REFUEL_THRESH:
        if refuel_from_inventory():
            pass
        else:
            print("Couldn't refuel! Uh oh...")

    return level


for count in range(MOVE_DISTANCE):

    check_fuel()

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
    turtle.down()

    if count % LIGHT_SEPARATION == 0:
        place_light_from_inventory()


# turn around after going up (so we dont break torches)

turtle.up()

turn_around()

for _ in range(MOVE_DISTANCE):
    turtle.forward()
    turtle.forward()

# turn around again
turtle.turnRight()
turtle.turnRight()
