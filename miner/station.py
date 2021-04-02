from cc import rednet
from cc import peripheral
from cc import parallel
from cc import import_file


def server_receive_broadcast():
    while True:
        info = rednet.receive("QuarryMiner")

        for each in range(len(info) // 3):
            each = each * 3
            computer_id, message, _ = info[each:each + 3]

            message = message.decode()

            print(f"\n> {message}")

        print("QuarryControl> ", end='')


def server_send_broadcast(message):
    rednet.broadcast(message.encode(), "QuarryControl")


def server_command_control():
    valid_commands = [
        "start",
        "stop"
    ]
    while True:
        command = input("QuarryControl> ")

        if command == "exit":
            print("Bye")
            break
        
        elif command == "ping":
            clients = rednet.lookup("QuarryMiner")

            if clients:
                print(f"Got response from {len(clients)} clients:")
                for client in clients:
                    print(f">  {client}")
            else:
                print("No clients available")

        elif command in valid_commands:
            server_send_broadcast(command)
        
        else:
            print("Invalid command. Valid commands are:")
            for command in valid_commands:
                print(f" - {command}")
            print()


def init():
    MODEM_SIDE = "back"

    if not rednet.isOpen(MODEM_SIDE):
        rednet.open(MODEM_SIDE)
        print("Opening modem")
    else:
        print("Modem is open")

    rednet.host("QuarryControl", "QuarryControl_C2")

    server_command_control()

    # parallel.waitForAny(server_command_control, server_receive_broadcast)

    rednet.unhost("QuarryControl")

    print("Closing modem")

    rednet.close(MODEM_SIDE)
