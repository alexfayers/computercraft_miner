import requests

JOIN_KEY = requests.get("http://192.168.1.54:8000/join.key").text


def init():
    print("WIP.")
