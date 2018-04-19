"""
    File name: cn1_mqtt.py
    Author: Georgios Vrettos
    Date created: 10/12/2017
    Date last modified: 16/12/2017
    Python Version: 2.7

In this module, functions from the package "paho-mqtt" are used. 
To install the package using pip issue the following command:
$pip install paho-mqtt 

Todo :
	* 
"""

import paho.mqtt.client as mqtt
import time
import ssl


# Global variables
# --------------------------------------------------------------------------------------------------
CA_CERT_PATH = "/home/vrettel/Dropbox/Thesis/Code/RaspberryPi/cn1_files/ca.crt"
BROKER_USERNAME = "username"
BROKER_PASSWORD = "password"
BROKER_IP = "ip_address"
BROKER_PORT = "8883"

# --------------------------------------------------------------------------------------------------

class Cn1Mqtt(mqtt.Client):
    'Class for the MQTT Raspberry Pi client node (cn1)'

    # Class functionality variables.

    # Signals the mqtt_function when a message is received.
    loop_flag = 1
    # The variable that holds the message.
    message = "null"
    #
    #XML_CONFIG_FILE = ""




    def on_connect(self,mqttc, userdata, flags, rc):
        """on_connect callback function. 
        This function is executed when the client connects successfully to the broker.
        Args:
            param1 (Client): The client instance.
            param2 (str): User defined data that is defined on Client().
            param3 (dict): The response flags from the broker.
            param4 (int): The result of the connection. 
            It indicates the connection status with a code (1-5)
        """

        print('Client connected. Return code=' + str(rc))
        # After a successfull connection, the client subscribes to a pecific topic
        #  by calling the subscribe function from the client package.


    def on_disconnect(self,mqttc, userdata, rc):
        """on_disconnect callback function. This function is executed
        when the client disconencts successfully from the broker.
        Args:
            param1 (Client): The client instance.
            param2 (str): User defined data that is defined on Client().
            param3 (dict): The response flags from the broker.
        """
        print('Client disconnected. Return code=' + str(rc))


    def on_message(self,mqttc, userdata, msg):
        """on_message callback function. 
        This function is executed when a message arrives (Someone published a message).
        Args:
            param1 (Client): The client instance.
            param2 (str): User defined data that is defined on Client().
            param3 (MQTTMessage): An instance of MQTTMessage, contains topic,payload,qos,retain
        """

        print('Message arrived...')
        # In the event of a message arrival, message content
        #is saved to the message variable
        Cn1Mqtt.message = msg

        #The loop flag becomes '0' and signals the mqtt_loop function to end.
        Cn1Mqtt.loop_flag = 0


    def on_publish(self,mqttc, userdata, mid):
        """on_publish callback function. 
        This function is executed when the client publishes a message successfully to a topic.
        Args:
            param1 (Client): The client instance.
            param2 (str): User defined data that is defined on Client().
            param3 (int): Mid is the message id. This id is compared with the mid 
            that function "publish()" returns in order to verify the message.
        """
        print('Published a message successfully')
        print("mid: " + str(mid))


    def on_subscribe(self,mqttc, userdata, mid, granted_qos):
        """on_subscribe callback function. 
        This function is executed when the client subscribes successfully to a topic.
        Args:
            param1 (Client): The client instance.
            param2 (str): User defined data that is defined on Client().
            param3 (int): Mid is the message id. This id is compared with the mid 
            that function "subscribe()" returns in order to verify the message.
            param4 (List(int)): A list of integers containing the qos
            for the selected subscription requests
        """
        print('subscribed (qos=' + str(granted_qos) + ')')



    def on_unsubscribe(self,mqttc, userdata, mid, granted_qos):
        """on_unsubscribe callback function. This function is executed
        when the client unsubscribes successfully from a topic.
        Args:
            param1 (Client): The client instance.
            param2 (str): User defined data that is defined on Client().
            param3 (int): Mid is the message id. This id is compared with the mid 
            that function "subscribe()" returns in order to verify the message.
            param4 (List(int)): A list of integers 
            containing the qos for the selected subscription requests
        """
        print('unsubscribed (qos=' + str(granted_qos) + ')')


    def mqtt_connect(self):
        """mqtt_connect function. This function is used for the broker connection.
        Args:
            param1 (Client): The client instance.
        """
        # The username and password for the connection are set.
        self.username_pw_set(BROKER_USERNAME, password=BROKER_PASSWORD)

        # The SSL/TLS connection parameters are set.
        # We porvide the ca certificate path, the option(certificate required) and the tls version.
        self.tls_set(ca_certs=CA_CERT_PATH, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2)
        try:
            # connection to the broker using ip address and port.
            self.connect(BROKER_IP, port=BROKER_PORT)
        except:
            # if the connection fails...
            print("Connection failed.")


    def mqtt_loop(self):
        """mqtt_loop function. This function is used for the MQTT network loop.
        The incoming message is saved from the mqtt buffer after the execution of
        a loop function.
        Args:
            param1 (Client): The client instance.
        """
        # Starting the loop
        self.loop_start()
        # The loop continues as long as there are no incomming messages.
        # It keeps the connection alive, waiting for messages.
        while Cn1Mqtt.loop_flag == 1:
            time.sleep(.01)
        # When a new message arrives, the loop breaks in order to handle the message
        self.loop_stop()
        # Flag resets back to 1 for the new loop.
        Cn1Mqtt.loop_flag = 1




