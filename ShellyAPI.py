import paho.mqtt.client as mqtt
from time import sleep

class ShellyPlug():

    def _add_topic(self, topic_name, topic_path, should_subscribe_to, should_publish_in):
        self.TOPICS[topic_name] =  {"topic_path":topic_path, "should_subscribe_to":should_subscribe_to, "should_publish_in":should_publish_in}
        self.TOPIC_TO_DESCRIPTION[topic_path] = topic_name
        
    def __init__(self, broker_hostname, model, devID, on_msg_callback):

        if model!="shellyplug" and model!="shellyplug-s":
            raise IllegalArgumentException("Unknown model")


        self.MQTT_ERRORS = {1:"Connection refused, unacceptable protocol version",
        2:"Connection refused, identifier rejected",
        3:"Connection refused, server unavailable",
        4:"Connection refused, bad user name or password",
        5:"Connection refused, not authorized"}

        self.HOSTNAME = broker_hostname
        self.MYID = f"ShellyManager-{model}-{devID}"
        self.TOPICS = {}
        self.TOPIC_TO_DESCRIPTION = {}
        self.on_msg_callback = on_msg_callback
        #self._add_topic("Will", "", False, True)

        self._add_all_topics(model, devID)

        self.model = model
        self.devID = devID

        self.client = mqtt.Client(self.MYID)


        def on_message(client, userdata, msg):
            self.on_msg_callback(self.TOPIC_TO_DESCRIPTION[msg.topic], msg.topic, msg.payload.decode())

        def on_connect(client, userdata, flags, rc):
            if rc != 0:
                raise ConnectionError(f"Could not connect to MQTT Broker, return code: {rc}")
            self.subscribe_to_all_topics(client)


        self.client.on_message = on_message
        self.client.on_connect = on_connect
        try:
            self.client.connect(broker_hostname)
        except ConnectionRefusedError as e:
            raise ConnectionError(f"Could not connect to MQTT Broker: Connection Refused")

        self.client.loop_start()

    def _add_all_topics(self, model, deviceid):
        self._add_topic("Status Report", f"shellies/{model}-{deviceid}/relay/0", True, False)
        self._add_topic("Instanteous Power Consumption (Watts)", f"shellies/{model}-{deviceid}/relay/0/power", True, False)
        self._add_topic("Energy Consumed (Watt/Minute)", f"shellies/{model}-{deviceid}/relay/0/energy", True, False)
        self._add_topic("Value When Overpower Detected (Watts)", f"shellies/{model}-{deviceid}/relay/0/overpower_value", True, False)

        if model=="shellyplug-s":
            self._add_topic("Temperature (C)", f"shellies/{model}-{deviceid}/temperature", True, False)
            self._add_topic("Temperature (F)", f"shellies/{model}-{deviceid}/temperature_f", True, False)
            self._add_topic("Did overheat (1 | 0)", f"shellies/{model}-{deviceid}/overtemperature", True, False)
            self._add_topic("Did overheat (1 | 0)", f"shellies/{model}-{deviceid}/online", True, False)

        self._add_topic("Send Command (on | off | toggle)", f"shellies/{model}-{deviceid}/relay/0/command", False, True)

        #Technical description so that sending command would be easier
        self._add_topic("send_command", f"shellies/{model}-{deviceid}/relay/0/command", False, True)


    def subscribe_to_all_topics(self, client):
        #print("Subscribing to topics..")
        for tpnm, topic in self.TOPICS.items():
            if topic["should_subscribe_to"]:
                client.subscribe(topic["topic_path"])

    def get_topics(self):
        return self.TOPICS

    def __del__(self):
        self.__class__.client.disconnect()
        self.__class__.client.loop_stop()

    '''
    Command can be one of the following:
    "on"
    "off"
    "toggle"
    '''
    def send_command(self, command):
        possible_commands = ["on", "off", "toggle"]
        if command not in possible_commands:
            raise IllegalArgumentException(f"The command is {command} which is not in {possible_commands}")

        topic = self.TOPICS["send_command"]["topic_path"]

        result = self.client.publish(topic, command)

        status = result[0]
        if status == 0:
            return True
        else:
            raise ConnectionError(f"Failed to send message to topic {topic}:\n {self.MQTT_ERRORS[status]}")






