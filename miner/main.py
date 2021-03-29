from cc import is_turtle, turtle
from cc import import_file

miner = import_file('miner.py', __file__)
station = import_file('station.py', __file__)

if not is_turtle():
    print("Running on a turtle - starting miner script!")
    miner.mine()
else:
    print("Running on a computer - starting station script!")
    station.init()

print("Python exit!")