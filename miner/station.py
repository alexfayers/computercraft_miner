from cc import rednet
from cc import peripheral
from cc import parallel
from cc import import_file


def server_receive_broadcast():
    while True:
        computer_id, message, _ = rednet.receive("QuarryMiner")

        message = message.decode()

        print(f"\n> {message}\n")


def server_send_broadcast(message):
    rednet.broadcast(message.encode(), "QuarryControl")


def server_command_control():
    while True:
        command = input("QuarryControl> ")

        if command == "exit":
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
