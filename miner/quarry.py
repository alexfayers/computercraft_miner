# uses gps to go to the correct place so need a modem

from cc import is_turtle, turtle
from cc import term
from cc import os

FUEL_TYPES = ["lava", "blaze", "coal", "wood"]
LIGHTING_TYPES = ["torch"]
CURSED_BLOCKS = ["lava", "water"]
GRAVITY_BLOCKS = ["gravel", "sand"]
DEPOSIT_BLOCKS = ["chest", "hopper"]

VALUEABLE_BLOCKS = [
    "ore",
    "diamond",
    "redstone",
    "iron",
    "gold",
    "lapis",
    "emerald",
    "flint",
]  # not coal, we wanna keep that

TRASH_BLOCKS = ["diorite", "granite", "andesite", "dirt", "cobble", "gravel", "sand"]

# Const type things
TURTLE_SLOTS = 16
CHUNK_SIZE = 16

REFUEL_THRESH = 20
FUEL_REQUIREMENT = CHUNK_SIZE * CHUNK_SIZE

term.clear()

if not os.getComputerLabel():
    os.setComputerLabel(f"Quarrybot #{os.getComputerID()}")

## functions


def turn_around():
    turtle.turnRight()
    turtle.turnRight()


def find_item(search):
    for slot in range(1, TURTLE_SLOTS + 1):
        info = turtle.getItemDetail(slot)

        if info is not None and search in info["name"]:
            return slot
    return False


def refuel_from_inventory():
    refueled = False

    foundFuel = False
    for fuel_type in FUEL_TYPES:
        fuel_slot = find_item(fuel_type)
        if fuel_slot:
            print(f"Found fuel in slot {fuel_slot}")

            foundFuel = True

            prevSlot = turtle.getSelectedSlot()
            turtle.select(fuel_slot)

            print(f"Refueling from slot {fuel_slot}...")
            if not turtle.refuel():
                break

            turtle.select(prevSlot)
            refueled = True
            break

    # give up
    if not foundFuel:
        print("Ran out of fuel :/")

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


def throw_away_trash():
    threw_away = False

    for block in TRASH_BLOCKS:
        while True:
            block_slot = find_item(block)
            if block_slot:
                prevSlot = turtle.getSelectedSlot()
                turtle.select(block_slot)

                turtle.dropUp()

                turtle.select(prevSlot)

                print(f"Dropped some {block} (trash block)")

                threw_away = True
            else:
                break

    return threw_away


def deposit_valueables():
    canDeposit = False
    for block in DEPOSIT_BLOCKS:
        info = turtle.inspect()

        if info is not None and block in info["name"]:
            print(f"found deposit block!")
            canDeposit = True
            break

    if canDeposit:
        deposit_count = 0

        while True:
            deposited = False

            for block in VALUEABLE_BLOCKS:
                block_slot = find_item(block)

                if block_slot:
                    prevSlot = turtle.getSelectedSlot()
                    turtle.select(block_slot)

                    turtle.drop()  # drop the items into the chest or whatever

                    turtle.select(prevSlot)

                    print(f"Deposited some {block} into storage")

                    # notify("Deposit", f"Deposited {block} into storage")

                    deposit_count += 1

                    deposited = True

            if not deposited:
                print("Didn't deposit anything this run, breaking.")

                sort_inventory()
                break

        return True

    else:
        print("Can't deposit in this block!")

    return False


def get_items_from_in_front(number):
    success = False
    if turtle.suck(number):
        success = True
    sort_inventory()

    return success


def get_fuel_from_chest():
    target_fuel_count = FUEL_REQUIREMENT

    for fuel_type in LIGHTING_TYPES:
        fuel_slot = find_item(fuel_type)
        item_count = 0
        if fuel_slot:
            item_count = turtle.getItemCount(fuel_slot)

        if item_count < target_fuel_count:
            fuel_needed = target_fuel_count - item_count
            print(f"Need fuel - getting {fuel_needed}")
            turtle.turnLeft()
            if not get_items_from_in_front(fuel_needed):
                print("Couldn't get enought fuel")
                # notify("Not enough fuel", "Uh oh")
            turtle.turnRight()


def status_check():
    # checks to make sure everytjing is going well
    throw_away_trash()
    check_fuel()


def dig_step():
    if turtle.detect():
        turtle.dig()

    if turtle.detectDown():
        turtle.digDown()


def mine_line(current_line_number):
    for block in range(CHUNK_SIZE - 1):
        status_check()

        dig_step()

        turtle.forward()

    status_check()

    dig_step()

    print(f"Finished line {current_line_number}")


def next_line(current_line_number):
    if current_line_number % 2 == 0:
        turtle.turnLeft()
        turtle.forward()
        turtle.turnLeft()
    else:
        turtle.turnRight()
        turtle.forward()
        turtle.turnRight()


def mine_layer():
    for line_number in range(CHUNK_SIZE - 1):
        mine_line(line_number)
        next_line(line_number)


def mine():
    while turtle.getFuelLevel() < FUEL_REQUIREMENT:
        get_fuel_from_chest()
        if not refuel_from_inventory():
            print("Ran out of fuel in chest probs")
            break  # used up da fuel
    mine_layer()
