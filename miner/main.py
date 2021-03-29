from cc import is_turtle, turtle
from cc import import_file


if not is_turtle():
    print("Running on a turtle - starting miner script!")
    miner = import_file('miner.py', __file__)
    miner.mine()
else:
    print("Running on a computer - starting station script!")
    station = import_file('station.py', __file__)
    station.init()

print("Python exit!")