"""
    File name: sn_mqtt.py
    Author: Georgios Vrettos
    Date created: 11/12/2017
    Date last modified: 19/4/2018
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
from sn_thread import Sn_thread

# Global variables
# --------------------------------------------------------------------------------------------------
CA_CERT_PATH = "/home/vrettel/Dropbox/Thesis/Code/PC Server/sn_files/ca.crt"
BROKER_USERNAME = "username"
BROKER_PASSWORD = "password"
BROKER_IP = "ip"
BROKER_PORT = "8883"

# --------------------------------------------------------------------------------------------------


class SnMqtt(mqtt.Client):
    'Base class for the MQTT client (SN)'

    # Class functionality variables.
    # A message buffer
    buffer = []



    def on_connect(self,mqttc, userdata, flags, rc):
        """on_connect callback function. 
        This function is executed when the client connects successfully to the broker.
        Args:
            param1 (Client): The client instance.
            param2 (str): User defined data that is defined on Client().
            param3 (dict): The response flags from the broker.
            param4 (int): The result of the connection. It indicates the connection status with a code (1-5)
        """

        print('SN connected. Return code=' + str(rc))

    def on_disconnect(self,mqttc, userdata, rc):
        """on_disconnect callback function. This function is executed
        when the client disconencts successfully from the broker.
        Args:
            param1 (Client): The client instance.
            param2 (str): User defined data that is defined on Client().
            param3 (dict): The response flags from the broker.
        """
        print('SN disconnected. Return code=' + str(rc))


    def on_message(self,mqttc, userdata, msg):
        """on_message callback function. 
        This function is executed when a message arrives (Someone published a message).
        Args:
            param1 (Client): The client instance.
            param2 (str): User defined data that is defined on Client().
            param3 (MQTTMessage): An instance of MQTTMessage, contains topic,payload,qos,retain
        """

        # In the event of a message arrival, the message is added to the buffer
        self.buffer.append(msg)



    def on_publish(self,mqttc, userdata, mid):
        """on_publish callback function. 
        This function is executed when the client publishes a message successfully to a topic.
        Args:
            param1 (Client): The client instance.
            param2 (str): User defined data that is defined on Client().
            param3 (int): Mid is the message id. This id is compared with the mid 
            that function "publish()" returns in order to verify the message.
        """
        #print('Published message.')
        #print("mid: " + str(mid))



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

    def on_unsubscribe(self,mqttc, mid, granted_qos):
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
        The incoming message is saved from the broker's buffer after the execution of
        a loop function.
        Args:
            param1 (Client): The client instance.
        """

        # Starting the loop
        self.loop_start()






