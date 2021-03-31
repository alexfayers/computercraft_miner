# uses gps to go to the correct place so need a modem

from cc import is_turtle, turtle
from cc import term
from cc import os
from cc import peripheral

import math

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
    "clay",
    "root",
]  # not coal, we wanna keep that


# CONFIG
CHUNK_SIZE = 8
QUARRY_DEPTH = 15
REFUEL_THRESH = 20
QUARRY_DEPTH_SKIP = 0

# Const type things
TURTLE_SLOTS = 16
FUEL_REQUIREMENT = (
    CHUNK_SIZE * CHUNK_SIZE * (QUARRY_DEPTH - QUARRY_DEPTH_SKIP)
    + QUARRY_DEPTH
    + CHUNK_SIZE * 2
)

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

        if info is not None and search.encode() in info[b"name"]:
            return slot
    return False


def refuel_from_inventory():
    refueled = False

    foundFuel = False
    for fuel_type in FUEL_TYPES:
        fuel_slot = 1
        while fuel_slot:
            fuel_slot = find_item(fuel_type)
            if fuel_slot:
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

    for slot in range(1, TURTLE_SLOTS + 1):
        slotinfo = turtle.getItemDetail(slot)

        if slotinfo is not None and not any(
            search.encode() in slotinfo[b"name"]
            for search in VALUEABLE_BLOCKS + FUEL_TYPES
        ):  # if not valuable or fuel, drop it
            prevSlot = turtle.getSelectedSlot()
            turtle.select(slot)

            turtle.dropUp()

            turtle.select(prevSlot)
            # print(f"Dropped some {slotinfo['name']} (non-valuable block)")


def deposit_valueables():
    canDeposit = False
    for block in DEPOSIT_BLOCKS:
        info = turtle.inspect()

        if info is not None and block.encode() in info[b"name"]:
            print(f"Found deposit block!")
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


def deposit_valueables_into_network():
    canDeposit = False
    for block in DEPOSIT_BLOCKS:
        info = turtle.inspect()

        if info is not None and block.encode() in info[b"name"]:
            print(f"Found deposit block!")
            canDeposit = True
            break

    if canDeposit:
        deposit_count = 0

        while True:
            deposited = False

            for block in VALUEABLE_BLOCKS:
                block_slot = find_item(block)

                if block_slot:
                    amount = locate_space_and_put_in_network(
                        block_slot
                    )  # drop the items into the chest or whatever

                    if amount <= 0:
                        print("Couldn't deposit anything")
                        deposited = False
                        break

                    print(f"Deposited {amount} {block} into storage")

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

    if number >= 255:
        for _ in range(number // 255 + number % 255):
            if turtle.suck(number):
                success = True
            else:
                success = False
                break
    else:
        if turtle.suck(number):
            success = True

    sort_inventory()

    return success


def get_fuel_from_chest(target_fuel_count):

    for fuel_type in LIGHTING_TYPES:
        fuel_slot = find_item(fuel_type)
        item_count = 0
        if fuel_slot:
            item_count = turtle.getItemCount(fuel_slot)

        if item_count < target_fuel_count:
            fuel_needed = target_fuel_count - item_count
            print(f"Getting {fuel_needed} items")
            turtle.turnLeft()
            if not get_items_from_in_front(fuel_needed):
                print("Couldn't get enought fuel")
                exit()
                # notify("Not enough fuel", "Uh oh")
            turtle.turnRight()


def status_check():
    # checks to make sure everytjing is going well
    throw_away_trash()
    sort_inventory()
    check_fuel()


def dig_step():
    if turtle.detect():
        turtle.dig()

    # if turtle.detectDown():
    #    turtle.digDown()


def down_layer():
    if turtle.detectDown():
        turtle.digDown()

    turtle.down()


def travel_line():
    for block in range(CHUNK_SIZE - 1):
        turtle.forward()


def mine_line(current_line_number):
    for block in range(CHUNK_SIZE - 1):
        dig_step()
        turtle.forward()


def next_line(current_line_number):
    if current_line_number % 2 == 0:
        turtle.turnRight()
        dig_step()
        turtle.forward()
        turtle.turnRight()
    else:
        turtle.turnLeft()
        dig_step()
        turtle.forward()
        turtle.turnLeft()


def mine_layer():
    for line_number in range(CHUNK_SIZE):
        status_check()
        mine_line(line_number)

        if line_number < CHUNK_SIZE - 1:
            next_line(line_number)


def mine_several_layers():
    for layer in range(QUARRY_DEPTH):
        mine_layer()

        if CHUNK_SIZE % 2 == 0:
            turtle.turnRight()
        else:
            turtle.turnLeft()

        if layer < QUARRY_DEPTH - 1:
            down_layer()

        print(f"Layer {layer} complete")


def return_to_start():
    corner = QUARRY_DEPTH % 4

    if corner == 1:
        travel_line()
    elif corner == 2:
        travel_line()
        turtle.turnRight()
        travel_line()
    elif corner == 3:
        turtle.turnRight()
        travel_line()

    for layer in range(QUARRY_DEPTH - 1):
        turtle.up()

    if corner == 1:
        turtle.turnRight()
    elif corner == 2:
        turtle.turnRight()
    elif corner == 3:
        turn_around()


def skip_layers():
    for _ in range(QUARRY_DEPTH_SKIP):
        down_layer()


def locate_item_in_network(search):
    try:
        network = peripheral.wrap("right")
    except:
        print("No modem to the right of the turtle!")
        return ()

    for device in network.getNamesRemote():
        print("Found storage device")

        if "chest" in device:
            chest = peripheral.wrap(device)

            for slot, item in chest.list().items():
                if search.encode() in item[b"name"]:
                    print(
                        f"Found {item[b'count']} {search} in slot {slot} in {device}!"
                    )
                    return (device, slot, item[b"count"])

            return ()


def locate_empty_storage_in_network(search):
    try:
        network = peripheral.wrap("right")
    except:
        print("No modem to the right of the turtle!")
        return ()

    for device in network.getNamesRemote():

        if "chest" in device:
            chest = peripheral.wrap(device)

            if len(chest.list()) < chest.size():
                return device
            else:
                return None


def get_from_network(storage_name, from_slot, count=64):
    try:
        network = peripheral.wrap("right")
    except:
        print("No modem to the right of the turtle!")
        return 0

    try:
        turtle_name = network.getNameLocal()
    except:
        print("Turtle is not connected to network!")
        return 0

    try:
        storage = peripheral.wrap(storage_name)
    except:
        print(f"peripheral {storage_name} doesn't exist!")
        return 0

    print(f"Fetching {count} items from slot {from_slot}!")

    return storage.pushItems(turtle_name, from_slot, count)


def put_in_network(storage_name, from_slot, count=64):
    try:
        network = peripheral.wrap("right")
    except:
        print("No modem to the right of the turtle!")
        return 0

    try:
        turtle_name = network.getNameLocal()
    except:
        print("Turtle is not connected to network!")
        return 0

    try:
        storage = peripheral.wrap(storage_name)
    except:
        print(f"peripheral {storage_name} doesn't exist!")
        return 0

    print(f"Attempting to put {count} items from slot {from_slot}!")

    return storage.pullItems(turtle_name, from_slot, count)


def locate_and_get_from_network(search, target_count=64):

    got_count = 0
    fuel_slot = find_item(search)
    if fuel_slot:
        got_count = turtle.getItemCount(fuel_slot)

    while got_count < target_count:
        print(got_count)
        item_location = locate_item_in_network(search)
        if item_location:
            storage_name, fuel_slot, fuel_amount = item_location

            fetch_amount = (target_count - got_count) // 64 + (
                target_count - got_count
            ) % 64

            if fetch_amount > fuel_amount:
                fetch_amount = fuel_amount

            if not get_from_network(storage_name, fuel_slot, count=fetch_amount):
                return False

            got_count += fetch_amount
        else:
            return False

    return True


def locate_space_and_put_in_network(from_slot):
    # storage_name = locate_empty_storage_in_network(item_name)
    storage_names = []
    transferred = 0
    try:
        network = peripheral.wrap("right")
    except:
        print("No modem to the right of the turtle!")
        return ()

    for device in network.getNamesRemote():
        if "chest" in device:
            transferred += put_in_network(device, from_slot)

    print(f"Tranferred {transferred} items into storage")

    return transferred


def mine():
    target_fuel_count = math.ceil(FUEL_REQUIREMENT // 80)  # 80 is coal amount

    print(
        f"Require {FUEL_REQUIREMENT} fuel for this job ({target_fuel_count} coal total). I have {turtle.getFuelLevel()} fuel..."
    )

    while turtle.getFuelLevel() < FUEL_REQUIREMENT:
        print("REFUELING!!!")
        if not locate_and_get_from_network("coal", target_fuel_count):
            refuel_from_inventory()
            break
        refuel_from_inventory()

    while turtle.getFuelLevel() < FUEL_REQUIREMENT:
        print("REFUELING!!!")
        get_fuel_from_chest(target_fuel_count)
        refuel_from_inventory()

    print("Got enough fuel, we're off!")

    if QUARRY_DEPTH_SKIP > 0:
        print("Skipping some layers...")
        skip_layers()
        print("Starting properly!")

    mine_several_layers()

    print("Returning to start...")
    return_to_start()

    turn_around()
    deposit_valueables()
    turn_around()

    print("Run complete")
