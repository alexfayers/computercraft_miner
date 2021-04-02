from cc import rednet
from cc import peripheral
from cc import parallel
from cc import import_file


def server_receive_broadcast():
    while True:
        for message in rednet.receive("QuarryMiner":
            print(repr(msg))


def server_send_broadcast(message):
    rednet.broadcast(message, "QuarryControl")


def server_command_control():
    while True:
        command = input("QuarryControl> ").encode()

        if command == b"exit":
            print("Bye")
            break

        server_send_broadcast(command)


def init():
    MODEM_SIDE = "back"

    if not rednet.isOpen(MODEM_SIDE):
        rednet.open(MODEM_SIDE)
        print("Opening modem")
    else:
        print("Modem is open")

    parallel.waitForAny(server_command_control, server_receive_broadcast)

    print("Closing modem")

    rednet.close(MODEM_SIDE)
