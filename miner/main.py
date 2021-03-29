from cc import is_turtle, turtle

import station
import turtle

if not is_turtle():
    print("Running on a turtle - starting miner script!")
    turtle.mine()
else:
    print("Running on a computer - starting station script!")
    station.init()

print("Python exit!")