from ShellyAPI import ShellyPlug
from time import sleep

def my_on_message(description, topic, payload):
    print(f"Received `{payload}` from `{description}` topic")


print("Creating ShellyPlug object..")
shp = ShellyPlug("192.168.0.188", "shellyplug-s", "6E9202", my_on_message)

print("Switching it off..")
shp.send_command("off")
sleep(3)
print("Switching it on..")
shp.send_command("on")

print("Whiling..")
while True:
    sleep(1)
