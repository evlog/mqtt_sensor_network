"""
    File name: cn2_mqtt.py
    Author: Georgios Vrettos
    Date created: 6/1/2018
    Date last modified: 13/3/2018
    Micropython Version: 1.9.3


This module contains the functions used for the MQTT connection.

Todo :
	* 

"""

from simple import MQTTClient
import time



# Global variables
# --------------------------------------------------------------------------------------------------
#CA_CERT_PATH = "/ca.crt" # Not currently used
BROKER_USERNAME = "IoT_thesis"
BROKER_PASSWORD = "1234#2017"
BROKER_IP = "195.251.166.202"
BROKER_PORT = 8883

# --------------------------------------------------------------------------------------------------

class Cn2Mqtt():
    """
    This class serves as a bridge between the mqtt part of the program and the rest of the code.
    It is used to serve all basic functions needed in the network.
    """

    # Class functionality variables.

    # This variable holds the mqtt connection.
    mqtt = None

    # The topic and the payload of the incoming message.
    r_topic = None
    r_message = None

    def connect(self):
        """ connect function. This function is used to connect ESP8266 to the MQTT network.
        """
        state = 0
        while state != 2:
            try:
                # connection object instance
                self.mqtt = MQTTClient(client_id="CN2", server=BROKER_IP, port=BROKER_PORT,
                                       user=BROKER_USERNAME, password=BROKER_PASSWORD, ssl=True)
                # connection to network
                self.mqtt.connect()
                state = 2
            except:
                print('Error connecting to the broker')
                time.sleep(0.5)
                continue

        print("Connected to MQTT network")
        # Set function "on_message" to work as a callback.
        self.mqtt.set_callback(self.on_message)


    def standby_loop(self):
        """ standby_loop function. This function the basic looping function for every
            incomming MQTT message.
        """

        if True:
            # Blocking wait for message
            self.mqtt.wait_msg()


    def on_message(self, topic, msg):
        """on_message function. This function runs when a new message arrives.
        Args:
            param1 (byte): The message topic in byte format.
            param2 (byte): The message payload in byte format.
        """
        print("Message arrived...")
        # class variables are set in order to share the message with other classes
        Cn2Mqtt.r_topic = topic.decode("utf-8")
        Cn2Mqtt.r_message = msg.decode("utf-8")


    def publish(self,topic, msg, retain, qos):
        """publish function. This function is used to publish a message.
        Args:
            param1 (str): The message topic.
            param2 (str): The message payload.
            param3 (Boolean): Retain flag.
            param4 (int): The qos level.
        """
        self.mqtt.publish(topic, msg, retain, qos)
        print("Message published successfully.")

    def subscribe(self, topic, qos):
        """subscribe function. This function is used to publish a message.
        Args:
            param1 (str): The message topic.
            param2 (int): The qos level.
        """
        self.mqtt.subscribe(topic, qos)
        print("Subscribed to topic: " + topic)

    def disconnect(self):
        """ disconnect function. This function is used to disconnect ESP8266 from the MQTT network.
        """
        print("Disconnecting from Broker")
        self.mqtt.disconnect()









