from cc import is_turtle, turtle
from cc import import_file
from cc import fs


if is_turtle():
    print("Running on a turtle - starting miner script!")

    if 1 == 2 and input("quarry or strip? (q/s): ").lower() == "s":
        miner = import_file("miner.py", __file__)
        miner.mine()
    else:
        miner = import_file("quarry.py", __file__)
        miner.init()
else:
    print("Running on a computer - starting station script!")
    station = import_file("station.py", __file__)
    station.init()

print("Python exit!")

# write the success file
with fs.open("/miner_success", "w") as f:
    f.writeLine("placeholder")
