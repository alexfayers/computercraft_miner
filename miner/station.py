from cc import rednet
from cc import peripheral

import requests

JOIN_KEY = requests.get("http://192.168.1.54:8000/join.key").text


def init():
    MODEM_SIDE = 'right'

    modem = peripheral.wrap(side)
    modem_name = modem.getName()

    if not rednet.isOpen(modem_name):
        rednet.open(modem_name)
    
    while True:
        command = input("QuarryControl> ")

        if command == 'exit':
            print("Bye")
            break

        rednet.broadcast(command, "QuarryControl")

    rednet.close(modem_name)
`
