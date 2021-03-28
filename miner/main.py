from cc import is_turtle, turtle
from cc import term

MOVE_DISTANCE = 10
REFUEL_THRESH = 20
FUEL_SATISFIED_THRESH = 200
LIGHT_SEPARATION = 16

BRANCH_COUNT = 2
BRANCH_SEPARATION = 2

FUEL_TYPES = ["lava", "blaze", "coal", "wood"]
LIGHTING_TYPES = ["torch"]

CURSED_BLOCKS = ["gravel", "lava"]

DEPOSIT_BLOCKS = ["chest", "hopper"]

VALUEABLE_BLOCKS = ["ore"]

# Const type things
TURTLE_SLOTS = 16

# Global updated tings

DISTANCE_COVERED = 0


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
    print("Attemping to place a light...")
    for lighting_type in LIGHTING_TYPES:
        light_slot = find_item(lighting_type)
        if light_slot:
            prevSlot = turtle.getSelectedSlot()
            turtle.select(light_slot)

            turn_around()
            turtle.place()
            turn_around()

            turtle.select(prevSlot)

            print("Light placed!")

            return True
    print("Light place failed :/")
    return False


def refuel_from_inventory():
    doRefuel = True
    refueled = False

    while doRefuel:

        foundFuel = False
        for fuel_type in FUEL_TYPES:
            fuel_slot = find_item(fuel_type)
            if fuel_slot:
                print(f"Found fuel in slot {fuel_slot}")

                foundFuel = True

                prevSlot = turtle.getSelectedSlot()
                turtle.select(fuel_slot)

                while turtle.getFuelLevel() <= FUEL_SATISFIED_THRESH:
                    print(f"Refueling from slot {fuel_slot}...")
                    if not turtle.refuel(1):
                        print(
                            "Run out of fuel in this slot, rescanning inventory for more."
                        )
                        break

                turtle.select(prevSlot)

                refueled = True
                doRefuel = False
                break

        # give up
        if not foundFuel:
            print("Ran out of fuel :/")
            doRefuel = False

    return refueled


def check_fuel():
    level = turtle.getFuelLevel()

    if level <= REFUEL_THRESH:
        print("Need to refuel!")

        if refuel_from_inventory():
            print("Refueled successfully!")
        else:
            print("Couldn't refuel! Uh oh...")
    else:
        pass
        # print("No need to refuel.")

    return level


def forward_and_check_lights():
    global DISTANCE_COVERED

    if turtle.detect():
        if not check_if_cursed_block():
            turtle.dig()
        else:
            return False

    turtle.forward()

    DISTANCE_COVERED += 1

    if DISTANCE_COVERED % LIGHT_SEPARATION == 0:
        place_light_from_inventory()

    print(f"Move forward ({DISTANCE_COVERED})")

    return True


def check_if_cursed_block():
    for block in CURSED_BLOCKS:
        info = turtle.inspect()

        if info is not None and block in info["name"]:
            print("CURSED BLOCK, ABANDON BRANCH!!!")
            return True
    return False


def check_valueable_up():
    for block in VALUEABLE_BLOCKS:
        info = turtle.inspectUp()

        if info is not None and block in info["name"]:
            turtle.digUp()
            print(f"Got valueable block ({info['name']})!")


def check_valueable_down():
    for block in VALUEABLE_BLOCKS:
        info = turtle.inspectDown()

        if info is not None and block in info["name"]:
            turtle.digDown()
            print(f"Got valueable block ({info['name']})!")


def check_valueable_left_right():
    turtle.turnLeft()

    for block in VALUEABLE_BLOCKS:
        info = turtle.inspect()

        if info is not None and block in info["name"]:
            turtle.dig()
            print(f"Got valueable block ({info['name']})!")

    turn_around()

    for block in VALUEABLE_BLOCKS:
        info = turtle.inspect()

        if info is not None and block in info["name"]:
            turtle.dig()
            print(f"Got valueable block ({info['name']})!")

    turtle.turnLeft()


def mine_step(branch_number):
    check_fuel()

    if not forward_and_check_lights():
        return False
    check_valueable_left_right()
    check_valueable_down()

    if turtle.detectUp():
        turtle.digUp()
    turtle.up()

    check_valueable_left_right()
    check_valueable_up()

    if not forward_and_check_lights():
        return False
    check_valueable_left_right()
    check_valueable_up()

    if turtle.detectDown():
        turtle.digDown()
    turtle.down()

    check_valueable_left_right()
    check_valueable_down()

    if branch_number >= 0 and DISTANCE_COVERED == 2:
        place_light_from_inventory()

    return True


def return_step():
    check_fuel()
    turtle.forward()
    print("Forward")


def create_branch(branch_number):
    global DISTANCE_COVERED

    block_in_front = turtle.inspect()

    if block_in_front is not None and any(
        lighting_block in block_in_front["name"] for lighting_block in LIGHTING_TYPES
    ):
        # we've done this already, skip it
        return False

    DISTANCE_COVERED = 0
    # start branch
    for count in range(MOVE_DISTANCE // 2):
        if not mine_step(branch_number):
            break

    # head back

    print("Heading back!")

    turtle.up()
    turn_around()

    for _ in range(DISTANCE_COVERED):  # come back the distance that we came
        return_step()

    turn_around()
    turtle.down()

    return True


def deposit_valueables():
    canDeposit = False
    for block in DEPOSIT_BLOCKS:
        info = turtle.inspectDown()

        if info is not None and block in info["name"]:
            print(f"found deposit block!")
            canDeposit = True
            break

    deposited = False
    if canDeposit:
        for block in VALUEABLE_BLOCKS:
            block_slot = find_item(block)

            if block_slot:
                prevSlot = turtle.getSelectedSlot()
                turtle.select(block_slot)

                turtle.dropDown()  # drop the items into the chest or whatever

                turtle.select(prevSlot)

                print(f"Deposited some {block} into storage")

                deposited = True

        if not deposited:
            print("Didn't deposit anything. Better luck next time :/")
        return deposited

    else:

        print("Can't deposit in this block!")


branch_number = 0
failed_branches = 0
while branch_number < BRANCH_COUNT:
    print(f"STARTING BRANCH {branch_number + failed_branches + 1}!")

    if create_branch(branch_number):
        print(f"BRANCH {branch_number + failed_branches + 1} COMPLETE!")
        branch_number += 1
    else:
        print("Already mined this branch!")
        failed_branches += 1

    turtle.turnRight()

    # move along to new branch section
    for _ in range(BRANCH_SEPARATION):
        mine_step(-1)

    turtle.turnLeft()

print("Returning home!")

turtle.turnLeft()

for _ in range((BRANCH_SEPARATION + 1) * (branch_number + failed_branches + 1)):
    return_step()

turtle.turnRight()

print("Back!")

deposit_valueables()
