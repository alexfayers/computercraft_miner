from cc import rednet
from cc import peripheral
from cc import parallel
from cc import import_file
from cc import term


def server_receive_broadcast():
    while True:
        info = rednet.receive("QuarryMiner")

        for each in range(len(info) // 3):
            each = each * 3
            computer_id, message, _ = info[each : each + 3]

            message = message.decode()

            print(f"\n> {message}")

        print("QuarryControl> ", end="")


def server_send_broadcast(message):
    rednet.broadcast(message.encode(), "QuarryControl")


def update_clients():
    
    width, height = term.getSize()

    orig_x, orig_y = term.getCursorPos()

    status_message = f"Miners available: {len(rednet.lookup('QuarryMiner'))}"

    term.setCursorPos(width - len(status_message) - 1, 1)
    term.clearLine()
    term.write(status_message)

    term.setCursorPos(orig_x, orig_y)


def server_command_control():
    valid_commands = ["start", "start_opts", "stop", "kill", "help", "exit"]

    first_loop = True

    while True:
        update_clients()
        
        if not first_loop:
            command = input("QuarryControl> ")
        else:
            command = "ping"
            first_loop = False

        if command == "help":
            print("start - Start all miners with default params")
            print(
                "start_opts {START_Y} {END_Y} {HOLE_WIDTH_X} {HOLE_WIDTH_Z} - Start with params you specify"
            )
            print("stop - Stop all miners and make them return home (WIP)")
            print(
                "ping - Query which miners are on the network and available for commands"
            )
            print("kill - Kills execution on all available clients (very abruptly)")
            print("help - This message")
            print("exit - Exit the C2 (clients are unaffected)")

        elif command == "exit":
            print("Bye")
            break

        elif 1==2 and command == "ping":
            clients = rednet.lookup("QuarryMiner")

            if clients:
                print(f"{len(clients)} clients are online:")
                for client in clients:
                    print(f">  {client}")
            else:
                print("No clients available")

        elif command == "kill":
            if (
                input("Are you sure you want to kill all clients? (y/N): ").lower()
                == "y"
            ):
                server_send_broadcast(command)

        elif any(
            valid in command for valid in valid_commands
        ):  # if any of the valids are a substring of the input
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
