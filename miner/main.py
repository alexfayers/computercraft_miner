from cc import is_turtle, turtle

from miner import mine as turtle_mine
from station import init as station_init

if not is_turtle():
    print("Running on a turtle - starting miner script!")
    turtle_mine()
else:
    print("Running on a computer - starting station script!")
    station_init()

print("Python exit!")