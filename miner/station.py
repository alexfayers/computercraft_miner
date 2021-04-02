from cc import rednet
from cc import peripheral

import requests

JOIN_KEY = requests.get("http://192.168.1.54:8000/join.key").text


def init():
    MODEM_SIDE = "back"

    names = peripheral.getNames()
    print(names)
    modem_name = names[0]

    if not rednet.isOpen(modem_name):
        rednet.open(modem_name)

    while True:
        command = input("QuarryControl> ").encode()

        if command == b"exit":
            print("Bye")
            break

        rednet.broadcast(command, b"QuarryControl")

    rednet.close(modem_name)
