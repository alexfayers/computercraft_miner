from cc import rednet
from cc import peripheral
from cc import parallel

import requests

JOIN_KEY = requests.get("http://192.168.1.54:8000/join.key").text


def listen_for_response(modem_name):
    while True:
        response = rednet.receive("QuarryMiner"):
        if message == None:
            break
        else:
            for message in response:
                print(repr(msg))


def command_control(modem_name):
    while True:
        command = input("QuarryControl> ").encode()

        if command == b"exit":
            print("Bye")
            break

        rednet.broadcast(command, "QuarryControl")


def init():
    MODEM_SIDE = "back"

    names = peripheral.getNames()
    print(names)
    modem_name = names[0]

    if not rednet.isOpen(modem_name):
        rednet.open(modem_name)
        print("Opening modem")
    else:
        print("Modem is open")
    
    parallel.waitForAny(command_control, listen_for_response)

    print("Closing modem")

    rednet.close(modem_name)
