"""
    File name: cn2_mqtt.py
    Author: Georgios Vrettos
    Date created: 6/1/2018
    Date last modified: 6/1/2018
    Micropython Version: 1.9.3


This module contains the functions used for the MQTT connection.

Todo :
	* 

"""

from simple import MQTTClient
import time



# Global variables
# --------------------------------------------------------------------------------------------------
CA_CERT_PATH = "/ca.crt"
BROKER_USERNAME = "IoT_thesis"
BROKER_PASSWORD = "1234#2017"
BROKER_IP = "195.251.166.202"
BROKER_PORT = 1883

# --------------------------------------------------------------------------------------------------

class Cn2Mqtt():

    # Class functionality variables.

    # This variable holds the mqtt connection.
    mqtt = ""

    def connect(self):
        """ connect function. This function is used to connect ESP8266 to the MQTT network.
        """
        state = 0
        while state != 2:
            try:
                self.mqtt = MQTTClient(client_id="CN2", server=BROKER_IP, port=BROKER_PORT,
                                       user=BROKER_USERNAME, password=BROKER_PASSWORD, ssl=False)
                self.mqtt.connect()
                state = 2
            except:
                print('Error connecting to the broker')
                time.sleep(0.5)
                continue

        print("Connected to MQTT network")
        self.mqtt.set_callback(self.on_message)

    def on_message(self, topic, payload):
        print((topic, payload))


    def publish(self,topic, msg, retain, qos):
        self.mqtt.publish(topic, msg, retain, qos)
        print("Message published successfully.")

    def subscribe(self, topic, qos):
        self.mqtt.subscribe(topic, qos)
        print("Subscribed to topic: " + topic)









