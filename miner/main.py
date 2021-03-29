from cc import is_turtle, turtle
from cc import term
from cc import fs
from cc import os

import requests
import urllib
import math

MOVE_DISTANCE = 40
REFUEL_THRESH = 20
FUEL_SATISFIED_THRESH = 300
LIGHT_SEPARATION = 15

BRANCH_COUNT = 4
BRANCH_SEPARATION = 2

BLOCK_LOG_FILENAME = "block_log.csv"
LAST_BRANCH_FILE = "last_branch.txt"

JOIN_KEY = requests.get("http://192.168.1.54:8000/join.key").text

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

# Global updated tings

DISTANCE_COVERED = 0
PREVIOUS_VALUEABLE = ''


term.clear()

if not is_turtle():
    print("Turtle required!")
    exit()
else:
    if not os.getComputerLabel():
        os.setComputerLabel(f"Miner #{os.getComputerID()}")


def notify(title, text):
    title = f"{os.getComputerLabel()}: {title}"

    title = urllib.parse.quote_plus(title)
    text = urllib.parse.quote_plus(text)

    res = requests.get(
        f"https://joinjoaomgcd.appspot.com/_ah/api/messaging/v1/sendPush?deviceId=group.all&text={text}&title={title}&apikey={JOIN_KEY}"
    )


def turn_around():
    turtle.turnRight()
    turtle.turnRight()


def find_item(search):
    for slot in range(1, TURTLE_SLOTS + 1):
        info = turtle.getItemDetail(slot)

        if info is not None and search in info["name"]:
            return slot
    return False


def get_items_from_in_front(number):
    success = False
    if turtle.suck(number):
        success = True
    sort_inventory()

    return success


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
    notify("Ran out of lights", "Prepare for mobs")
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


def forward_and_check_cursed():
    global DISTANCE_COVERED

    if turtle.detect():
        if not check_if_cursed_block():
            turtle.dig()
        else:
            return False

        while check_if_gravity_block():
            turtle.dig()

    turtle.forward()

    DISTANCE_COVERED += 1

    print(f"Move forward ({DISTANCE_COVERED})")

    return True


def check_if_cursed_block():
    for block in CURSED_BLOCKS:
        info = turtle.inspect()

        if info is not None and block in info["name"]:
            print("CURSED BLOCK, ABANDON BRANCH!!!")

            notify("Cursed block!", "Found a cursed block, abandoning current branch")

            with fs.open(BLOCK_LOG_FILENAME, "a") as f:
                f.writeLine(f"{branch_number}, abandoned")

            return True
    return False


def check_if_gravity_block():
    for block in GRAVITY_BLOCKS:
        info = turtle.inspect()

        if info is not None and block in info["name"]:
            print("Gravity block!")

            return True
    return False


def block_log(branch_number, block_name):
    global PREVIOUS_VALUEABLE

    branch_number += 1

    print(f"Got valueable block ({block_name}) in branch {branch_number}!")

    if block_name != PREVIOUS_VALUEABLE: # dont notify is its the same
        notify(f"Found {block_name}", f"Found in branch {branch_number}")

    with fs.open(BLOCK_LOG_FILENAME, "a") as f:
        f.writeLine(f"{branch_number}, {block_name}")

    PREVIOUS_VALUEABLE = block_name


def place_cobble_under():
    block_slot = find_item('cobble')
    if block_slot:
        prevSlot = turtle.getSelectedSlot()
        turtle.select(block_slot)

        turtle.placeDown()

        turtle.select(prevSlot)


def check_valueable_up(branch_number):
    for block in VALUEABLE_BLOCKS:
        info = turtle.inspectUp()

        if info is not None and block in info["name"]:
            turtle.digUp()
            block_log(branch_number, info["name"])


def check_valueable_down(branch_number):
    for block in VALUEABLE_BLOCKS:
        info = turtle.inspectDown()

        if info is not None and block in info["name"]:
            turtle.digDown()
            place_cobble_under()
            block_log(branch_number, info["name"])

def sort_inventory():
    print("Sorting inventory")

    prevSlot = turtle.getSelectedSlot()

    for slot_number in range(TURTLE_SLOTS, 0, -1):
        turtle.select(slot_number)

        if not turtle.getItemCount():
            continue

        for new_slot_number in range(1, TURTLE_SLOTS, 1):
            if turtle.transferTo(new_slot_number):
                break
    
    turtle.select(prevSlot)

def throw_away_trash():
    threw_away = False
    for block in TRASH_BLOCKS:
        while True:
            block_slot = find_item(block)
            if block_slot:
                prevSlot = turtle.getSelectedSlot()
                turtle.select(block_slot)

                if 'cobble' in block and turtle.getItemCount() > 32:
                    print("Keeping some cobble for placing")
                    turtle.dropUp(turtle.getItemCount() - 32)
                else:
                    turtle.dropUp()

                turtle.select(prevSlot)

                print(f"Dropped some {block} (trash block)")

                threw_away = True
            else:
                break

    return threw_away


def check_valueable_left_right(branch_number):
    turtle.turnLeft()

    for block in VALUEABLE_BLOCKS:
        info = turtle.inspect()

        if info is not None and block in info["name"]:
            turtle.dig()
            block_log(branch_number, info["name"])

    turn_around()

    for block in VALUEABLE_BLOCKS:
        info = turtle.inspect()

        if info is not None and block in info["name"]:
            turtle.dig()
            block_log(branch_number, info["name"])

    turtle.turnLeft()


def mine_step(branch_number):
    check_fuel()

    if not forward_and_check_cursed():
        return False

    check_valueable_left_right(branch_number)
    check_valueable_down(branch_number)

    if turtle.detectUp():
        turtle.digUp()
    turtle.up()

    throw_away_trash()  # attempt to throw away trash while we're facing away

    check_valueable_left_right(branch_number)
    check_valueable_up(branch_number)

    if not forward_and_check_cursed():
        return False

    check_valueable_left_right(branch_number)
    check_valueable_up(branch_number)

    if turtle.detectDown():
        turtle.digDown()
    turtle.down()

    check_valueable_left_right(branch_number)
    check_valueable_down(branch_number)

    if branch_number >= 0 and (DISTANCE_COVERED == 2 or DISTANCE_COVERED % LIGHT_SEPARATION == 0):
        place_light_from_inventory()

    return True


def return_step():
    check_fuel()
    turtle.forward()


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

    if canDeposit:
        deposit_count = 0

        while True:
            deposited = False

            for block in VALUEABLE_BLOCKS:
                block_slot = find_item(block)

                if block_slot:
                    prevSlot = turtle.getSelectedSlot()
                    turtle.select(block_slot)

                    turtle.dropDown()  # drop the items into the chest or whatever

                    turtle.select(prevSlot)

                    print(f"Deposited some {block} into storage")

                    notify("Deposit", f"Deposited {block} into storage")

                    deposit_count += 1

                    deposited = True

            if not deposited:
                print("Didn't deposit anything this run, breaking.")
                break

        return True

    else:
        print("Can't deposit in this block!")

    return False


branch_number = 0
failed_branches = 0
latest_branch = 0

# check if need torches
target_light_count = int(math.ceil(MOVE_DISTANCE / LIGHT_SEPARATION)) * BRANCH_COUNT
for lighting_type in LIGHTING_TYPES:
    light_slot = find_item(lighting_type)
    item_count = 0
    if light_slot:
        item_count = turtle.getItemCount(light_slot)

    if item_count < target_light_count:
        lights_needed = target_light_count - item_count
        print(f"Need lights - getting {lights_needed}")
        turtle.turnLeft()
        if not get_items_from_in_front(lights_needed):
            print("Couldn't get enought lights")
            notify("Not enough lights", "Prepare for mobs")
        turtle.turnRight()

try:
    with fs.open(LAST_BRANCH_FILE, "r") as f:
        for line in f:
            latest_branch = line
            break
except Exception:
    print("Error opening status file. can be ignored usually.")
    pass

if latest_branch:
    latest_branch = int(latest_branch)
    print(f"Heading to branch {latest_branch}")
    turtle.turnRight()

    for _ in range(latest_branch):
        for _ in range(BRANCH_SEPARATION * 2):
            return_step()
        failed_branches += 1

    turtle.turnLeft()

    print("At latest branch, resuming normal behaviour")

while branch_number < BRANCH_COUNT:
    print(f"STARTING BRANCH {branch_number + failed_branches + 1}!")

    notify(
        "Branch update", f"Starting branch {branch_number + failed_branches + 1}"
    )

    if create_branch(branch_number + failed_branches):
        print(f"BRANCH {branch_number + failed_branches + 1} COMPLETE!")

        notify(
            "Branch update",
            f"Finished branch {branch_number + failed_branches + 1}",
        )

        branch_number += 1
    else:
        print("Already mined this branch!")
        failed_branches += 1

    with fs.open(LAST_BRANCH_FILE, "w") as f:
        f.writeLine(f"{branch_number + failed_branches}")

    turtle.turnRight()

    # move along to new branch section
    for _ in range(BRANCH_SEPARATION):
        mine_step(-1)

    turtle.turnLeft()

    sort_inventory()

print("Returning home!")

notify("Finished run", "Returning home now!")

turtle.turnLeft()

while True:
    # for _ in range((BRANCH_SEPARATION + 1) * (branch_number + failed_branches + 1)):
    return_step()
    if deposit_valueables():
        break

turtle.turnRight()

print("Back!")
