from ShellyAPI import ShellyPlug
from time import sleep
from datetime import datetime

def my_on_message(description, topic, payload):
    pass

print("Creating ShellyPlug object..")
shp = ShellyPlug("192.168.0.188", "shellyplug-s", "6E9202", my_on_message)

on="8:40"
off="22:10"

print("Whiling..")
while True:
    now = datetime.now()
    now_st = f"{now.hour}:{now.minute}"

    if now == on:
        print("Onning")
        shp.send_command("on")
    if now == off:
        print("Offing")
        shp.send_command("off")

    sleep(1)
