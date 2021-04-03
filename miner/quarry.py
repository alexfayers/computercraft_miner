# uses gps to go to the correct place so need a modem

from cc import turtle
from cc import term
from cc import os
from cc import peripheral
from cc import parallel
from cc import rednet
from cc import fs

import math
import requests
import urllib
import time

# TODO: Coords

FUEL_TYPES = ["lava", "blaze", "coal", "wood"]
LIGHTING_TYPES = ["torch"]
CURSED_BLOCKS = ["lava", "water"]
GRAVITY_BLOCKS = ["gravel", "sand"]
DEPOSIT_BLOCKS = ["modem"]  # "chest", "hopper"

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

HOLE_WIDTH_X = 8
HOLE_WIDTH_Z = 8


REFUEL_THRESH = 20

START_Y = 64  # inclusive
END_Y = 62  # non inclusive


# Const/non-config type things

DO_MINE = False

COORDS = {
    "x": 0,
    "y": 0,
    "z": 0,
    "heading": 0,  # 0 is forwards, 1 is right, 2 is back, 3 is left
}

TURTLE_SLOTS = 16

def generate_path(width_x, start_y, end_y, width_z):
    targets = []

    if start_y > end_y:
        y_diff = 1
    else:
        y_diff = -1

    for y in range(start_y, end_y + y_diff, y_diff):
        for x in range(0, (width_x), 2):
            print(x)
            targets.append({
            "x": x,
            "y": y,
            "z": 0
            })
            targets.append({
            "x": x,
            "y": y,
            "z": width_z - 1
            })
            targets.append({
            "x": x + 1,
            "y": y,
            "z": width_z - 1
            })
            targets.append({
            "x": x + 1,
            "y": y,
            "z": 0
            })

    return targets

# JOIN_KEY = requests.get("http://192.168.1.54:8000/join.key").text

term.clear()

if not os.getComputerLabel():
    os.setComputerLabel(f"Quarrybot_{os.getComputerID()}")

## functions


def calc_globals():
    global COORDS
    global FUEL_REQUIREMENT

    COORDS["y"] = START_Y

    quarry_depth = START_Y - END_Y

    FUEL_REQUIREMENT = (
        CHUNK_SIZE * CHUNK_SIZE * (quarry_depth) + quarry_depth + CHUNK_SIZE * 2
    )


def notify(title, text):
    text = f"{title}: {text}"
    title = f"{os.getComputerLabel()}"

    title = urllib.parse.quote_plus(title)
    text = urllib.parse.quote_plus(text)

    # res = requests.get(
    #    f"https://joinjoaomgcd.appspot.com/_ah/api/messaging/v1/sendPush?deviceId=group.all&text={text}&title={title}&apikey={JOIN_KEY}"
    # )

    res = requests.get(f"http://192.168.1.54:8081/?text={text}&title={title}")


def turn_right():
    global COORDS

    turtle.turnRight()
    COORDS["heading"] = (COORDS["heading"] + 1) % 4

    print(repr(COORDS))


def turn_left():
    global COORDS

    turtle.turnLeft()
    COORDS["heading"] = (COORDS["heading"] - 1) % 4

    print(repr(COORDS))


def forward(mine=False):
    global COORDS

    if not DO_MINE:
        return False

    if mine == True:
        while check_if_gravity_block_in_front():
            turtle.dig()

        if turtle.detect():
            turtle.dig()

    turtle.forward()

    if COORDS["heading"] == 0:  # forwards
        COORDS["z"] += 1
    elif COORDS["heading"] == 1:  # right
        COORDS["x"] += 1
    elif COORDS["heading"] == 2:  # backwards
        COORDS["z"] -= 1
    elif COORDS["heading"] == 3:  # left
        COORDS["x"] -= 1

    print(repr(COORDS))

    return True


def up(mine=False):
    global COORDS

    if not DO_MINE:
        return False

    if mine == True:
        while check_if_gravity_block_above():
            turtle.digUp()

        if turtle.detectUp():
            turtle.digUp()

    turtle.up()
    COORDS["y"] += 1

    print(repr(COORDS))

    return True


def down(mine=False):
    global COORDS

    if not DO_MINE:
        return False

    if mine == True:
        if turtle.detectDown():
            turtle.digDown()

    turtle.down()
    COORDS["y"] -= 1

    print(repr(COORDS))

    return True


def turn_around():
    turn_right()
    turn_right()


def turn_to_heading(target_heading):
    if target_heading == COORDS["heading"]:
        return

    while target_heading != COORDS["heading"]:
        if COORDS["heading"] < target_heading:
            if abs(COORDS["heading"] - target_heading) < 2:
                turn_right()
            else:
                turn_left()
        else:
            if abs(COORDS["heading"] - target_heading) < 2:
                turn_left()
            else:
                turn_right()

    return


def go_to_x(target_x, mine=False):
    if target_x != COORDS["x"]:
        if COORDS["x"] < target_x:
            turn_to_heading(1)  # right
        else:
            turn_to_heading(3)  # left

        while target_x != COORDS["x"]:
            if not forward(mine=mine):
                return False

    return True


def go_to_y(target_y, mine=False):
    while target_y != COORDS["y"]:
        if COORDS["y"] < target_y:
            if not up(mine=mine):
                return False
        else:
            if not down(mine=mine):
                return False

    return True


def go_to_z(target_z, mine=False):
    if target_z != COORDS["z"]:
        if COORDS["z"] < target_z:
            turn_to_heading(0)  # forward
        else:
            turn_to_heading(2)  # backward

        while target_z != COORDS["z"]:
            if not forward(mine=mine):
                return False

    return True


def go_to_coords(x=None, y=None, z=None, mine=False):
    if x is not None:
        if not go_to_x(x, mine=mine):
            return False

    if y is not None:
        if not go_to_y(y, mine=mine):
            return False

    if z is not None:
        if not go_to_z(z, mine=mine):
            return False

    return DO_MINE


def calc_distance_from_coords(x=None, y=None, z=None):
    if all(coord is not None for coord in [x,y,z]):
        distance = 0

        for index, coord in enumerate([COORDS["x"], COORDS["y"], COORDS["z"]]):
            distance = distance + abs(coord - [x,y,z][index])
        
        return distance
    else:
        return False


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

    usedSlots = 0
    for slot_number in range(TURTLE_SLOTS, 0, -1):
        if turtle.getItemCount(slot_number):
            usedSlots += 1

    if usedSlots <= TURTLE_SLOTS // 2:
        print("No need to sort, not half full/empty yet")
        return False

    for slot_number in reversed(range(1, TURTLE_SLOTS + 1)):
        if turtle.getItemCount(slot_number):
            turtle.select(slot_number)
            old_slot_details = turtle.getItemDetail(slot_number)
            if old_slot_details:
                if old_slot_details[b"count"] > 32:
                    print(f"not enough items to sort slot {slot_number} yet")
                    continue
                else:
                    item_name = old_slot_details[b"name"]
            print(f"sorting {item_name} in slot {slot_number}")
        else:
            print("next slot")
            continue

        print("finding slot")
        for new_slot_number in range(1, TURTLE_SLOTS + 1):
            slot_details = turtle.getItemDetail(new_slot_number)
            if (
                slot_details
                and slot_details[b"name"] == item_name
                and turtle.transferTo(new_slot_number)
            ):
                break

    turtle.select(prevSlot)

    return True


def check_fuel():
    print("Checking fuel")
    level = turtle.getFuelLevel()

    if level <= calc_distance_from_coords(x=0, y=START_Y, z=0):
        print("Not enough fuel to return!")

        if refuel_from_inventory():
            print("Refueled successfully!")#
            return True
        else:
            print("Couldn't refuel! Uh oh...")
            return False
    else:
        print("No need to refuel.")

    return True


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


def deposit_valueables_into_network():
    notify("Depositing valuables", "Lets goooooo")

    throw_away_trash()
    sort_inventory()

    desposits = []

    while True:
        deposited = False

        for block in VALUEABLE_BLOCKS + FUEL_TYPES:
            block_slot = find_item(block)

            if block_slot:
                amount = locate_space_and_put_in_network(
                    block_slot
                )  # drop the items into the chest or whatever

                if amount <= 0:
                    print("Couldn't deposit anything")
                    deposited = False
                    break

                desposits.append([amount, block])

                print(f"Deposited {amount} {block}")

                deposited = True

        if not deposited:
            # print("Didn't deposit anything this run, breaking.")

            # sort_inventory()
            break

    desposit_list = ""
    for deposit in desposits:
        desposit_list += f"{deposit[0]} - {deposit[1]}\n"

    if desposit_list:
        notify("Depositing valuables", f"Deposited the following:\n\n{desposit_list}")

    return deposited


def status_check():
    # checks to make sure everytjing is going well
    throw_away_trash()
    
    return check_fuel()


def check_if_gravity_block_in_front():
    for block in GRAVITY_BLOCKS:
        info = turtle.inspect()

        if info is not None and block.encode() in info[b"name"]:
            print("Gravity block!")

            return True
    return False


def check_if_gravity_block_above():
    for block in GRAVITY_BLOCKS:
        info = turtle.inspectUp()

        if info is not None and block.encode() in info[b"name"]:
            print("Gravity block!")

            return True
    return False


def dig_step():
    while check_if_gravity_block_in_front():
        turtle.dig()

    if turtle.detect():
        turtle.dig()

    # if turtle.detectDown():
    #    turtle.digDown()


def down_layer():
    hit_block = False

    if turtle.detectDown():
        turtle.digDown()
        hit_block = True

    down()

    return hit_block


def up_layer():
    hit_block = False

    if turtle.detectUp():
        turtle.digUp()
        hit_block = True

    up()

    return hit_block

def travel_line():
    for block in range(CHUNK_SIZE - 1):
        forward()


def mine_line(current_line_number):
    for block in range(CHUNK_SIZE - 1):
        dig_step()
        forward()


def next_line(current_line_number):
    if current_line_number % 2 == 0:
        turn_right()
        dig_step()
        forward()
        turn_right()
    else:
        turn_left()
        dig_step()
        forward()
        turn_left()


def mine_layer():
    for line_number in range(CHUNK_SIZE):
        status_check()
        mine_line(line_number)

        if line_number < CHUNK_SIZE - 1:
            next_line(line_number)
    sort_inventory()


def mine_several_layers():
    while END_Y <= COORDS["y"]:
        mine_layer()

        if CHUNK_SIZE % 2 == 0:
            turn_right()
        else:
            turn_left()

        if not DO_MINE:
            print("Stop signal was received, returing to start!")
            break

        print(f"y={COORDS['y']} complete")
        notify("Mining", f"y={COORDS['y']} complete (mining until y={END_Y})")

        if END_Y >= COORDS["y"]:
            break
        else:
            down_layer()

def mine_path():
    targets = generate_path(HOLE_WIDTH_X, COORDS["y"], END_Y, HOLE_WIDTH_Z)

    for target_index, target in enumerate(targets):
        x, y, z = target.values()

        if not status_check():
            break

        if not go_to_coords(x=x, y=y, z=z, mine=True): # returns false if stop was received
            return False

        if target_index % (HOLE_WIDTH_X * 2) == 0: # after each layer
            sort_inventory()
    
    return True


def return_to_start(skipped_layers, straight_up_override=False):
    corner = (START_Y - COORDS["y"] - skipped_layers) % 4
    notify("Mining", f"Returning home from y={COORDS['y']}")

    if straight_up_override:
        pass
    elif corner == 1:
        travel_line()
    elif corner == 2:
        travel_line()
        turn_right()
        travel_line()
    elif corner == 3:
        turn_right()
        travel_line()

    while COORDS["y"] < START_Y:
        # if up():
        up()

        # else:
        #    print("Failed to go upwards!")
        #    notify("Mining", "Failed returning because of an obstruction, exiting!")
        #    exit()

    if straight_up_override:
        pass
    elif corner == 1:
        turn_right()
    elif corner == 2:
        turn_right()
    elif corner == 3:
        turn_around()


def skip_layers():
    hit_block = False
    skipped = 0
    while COORDS["y"] > END_Y :
        hit_block = down_layer()
        if hit_block:
            print("Hit block, stopping layer skip")
            break
        skipped += 1
    
    while COORDS["y"] < END_Y :
        hit_block = up_layer()
        if hit_block:
            print("Hit block, stopping layer skip")
            break
        skipped += 1
    return hit_block, skipped


def locate_item_in_network(search):
    try:
        network = peripheral.wrap("left")
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
        network = peripheral.wrap("left")
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
        network = peripheral.wrap("left")
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
    except Exception as e:
        print(f"peripheral {storage_name} doesn't exist!")
        print(e)
        return 0

    print(f"Fetching {count} items from slot {from_slot}!")

    return storage.pushItems(turtle_name, from_slot, count)


def put_in_network(storage_name, from_slot, count=64):
    try:
        network = peripheral.wrap("left")
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

        print(item_location)
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
    transferred = 0
    try:
        network = peripheral.wrap("left")
    except:
        print("No modem to the left of the turtle!")
        return ()

    try:
        for device in network.getNamesRemote():
            print(device)
            if "chest" in device:
                transferred += put_in_network(device, from_slot)
    except:
        print("Error - probably no modem to the left")
        return 0

    print(f"Tranferred {transferred} items into storage")

    return transferred


def mine():
    global DO_MINE

    calc_globals()

    while True:
        notify("Ready", "Waiting for start signal")

        print("Waiting for start signal...")

        while not DO_MINE:
            print(
                "Waiting for start signal..."
            )  # apparently have to spam something so we can parallelise (maybe otherwise the server gets DOSed?)
            # time.sleep(1)
            pass

        print("Received mine signal!")

        target_fuel_count = math.ceil(FUEL_REQUIREMENT // 80)  # 80 is coal amount

        print(
            f"Require {FUEL_REQUIREMENT} fuel for this job ({target_fuel_count} coal total). I have {turtle.getFuelLevel()} fuel..."
        )

        cur_fuel = turtle.getFuelLevel()
        prev_fuel = -1

        if cur_fuel < FUEL_REQUIREMENT:
            notify(
                "Refueling",
                f"Need to refuel - current fuel is {cur_fuel} and requirement is {FUEL_REQUIREMENT}",
            )

        do_re_wait = False
        while cur_fuel < FUEL_REQUIREMENT:
            print(f"REFUELING ({cur_fuel})!!!")
            if not locate_and_get_from_network("coal", target_fuel_count):
                notify(
                    "Refueling",
                    f"Not enough fuel in network to reach requirement (have {cur_fuel}), exiting!",
                )
                print("Not enough fuel")
                do_re_wait = True
                break
            refuel_from_inventory()
            cur_fuel = turtle.getFuelLevel()

            if prev_fuel == cur_fuel and cur_fuel < FUEL_REQUIREMENT:
                # couldnt refuel
                print("Failed to refuel")
                notify("Refueling", "Failed to refuel to requirement, exiting!")
                do_re_wait = True
                break
            prev_fuel = cur_fuel

        if do_re_wait == True:
            DO_MINE = False
            continue

        print("Got enough fuel, we're off!")
        # notify("Refueling", "Refueling done!")

        # notify("Mining", "Starting floor detection")

        if COORDS["y"] != END_Y:
            print("Starting floor detection...")
            hit_block, skipped_layers = skip_layers()
        else:
            hit_block = True
            skipped_layers = 0

        if hit_block:
            print(f"Starting properly at y={COORDS['y']}!")
            notify("Mining", f"Starting mining at y={COORDS['y']}!")

            #mine_several_layers()
            if not mine_path(): # we've been told to return
                DO_MINE = True
        else:
            print("Didn't hit any blocks - all of this area is already mined")
            notify("Mining", "Didn't mine - didn't hit any blocks")

        print("Returning to start...")
        go_to_coords(x=0, y=START_Y, z=0, mine=True)

        turn_to_heading(0)

        # return_to_start(skipped_layers, straight_up_override=not hit_block)
        
        # turn_around()
        if hit_block:
            if not deposit_valueables_into_network():
                notify("Depositing valuables", "Didn't deposit anything")
        # turn_around()

        print("Run complete")

        DO_MINE = False


# networking stuff


def client_send_broadcast(message):
    rednet.broadcast(message.encode(), "QuarryMiner")
    print(f"Sent message")


def client_receive_broadcast():
    global DO_MINE
    global CHUNK_SIZE
    global HOLE_WIDTH_X
    global HOLE_WIDTH_Z
    global START_Y
    global END_Y

    while True:
        print("Receiving messages...")

        computer_id, message, _ = rednet.receive("QuarryControl")

        message = message.decode()

        print(f"\nReceived {message}\n")

        # if message == "ping":
        #    pass
        if "start_opts" in message:
            message = message.split(" ")

            if type(message) == list and len(message) >= 5:
                if all(item.isdigit() for item in message[1:5]):
                    START_Y = int(message[1])
                    END_Y = int(message[2])
                    HOLE_WIDTH_X = int(message[3])
                    HOLE_WIDTH_Z = int(message[4])
                    # CHUNK_SIZE = int(message[3])

                    calc_globals()
                    DO_MINE = True
                    notify(
                        "Config",
                        f"Mining from {START_Y} to {END_Y} with a size of {HOLE_WIDTH_X}x{HOLE_WIDTH_Z}",
                    )
                    continue

            notify(
                "Config",
                "Got start_opts but incorrect number of options or invalid options.",
            )
        elif message == "kill":
            notify("KILL", "Stopping execution via an exit")  # add cleanup here maybe
            exit()
        elif message == "update":
            notify("Update", "Stopping execution and updating")
            with fs.open('/miner_update', 'w') as f:
                f.writeLine('placeholder')
            exit()
        elif message == "start":
            DO_MINE = True
        elif message == "stop":
            if DO_MINE:
                notify("Mining", "Stop received, returning home")
            DO_MINE = False
        else:
            print("Received a non-valid command")


def init():

    MODEM_SIDE = "right"

    if not rednet.isOpen(MODEM_SIDE):
        rednet.open(MODEM_SIDE)
        print("Opening modem")
    else:
        print("Modem is open")

    rednet.host("QuarryMiner", os.getComputerLabel())

    parallel.waitForAny(mine, client_receive_broadcast)

    rednet.unhost("QuarryMiner")

    print("Closing modem")

    rednet.close(MODEM_SIDE)
