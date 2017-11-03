"""
    File name: mqtt_handler.py
    Author: Georgios Vrettos
    Date created: 01/11/2017
    Date last modified: 03/11/2017
    Python Version: 2.7

In this module, functions from the package "paho-mqtt" are used. To install the package using pip issue the following command:
$pip install paho-mqtt 

Example:
	$ python mqtt_handler.py

Todo :
	* Make the program object oriented using classes
	* Add Static variables such as ip, port etc
	* Add incoming messages to List or Dictionary (optional)
"""

import paho.mqtt.client as mqtt
import time
import database_handler as db


# Global variables
# --------------------------------------------------------------------------------------------------


# --------------------------------------------------------------------------------------------------


def on_connect(mqttc, userdata, flags, rc):
    """on_connect callback function. This function is executed when the client connects successfully to the broker.
    Args:
        param1 (Client): The client instance.
        param2 (str): User defined data that is defined on Client().
        param3 (dict): The response flags from the broker.
        param4 (int): The result of the connection. It indicates the connection status with a code (1-5)
    """
    print('Client connected. Return code=' + str(rc))
    #After a successfull connection, the client subscribes to a pecific topic by calling the subscribe function from the client package.
    mqttc.subscribe(topic='devices/+/+', qos=0)


def on_disconnect(mqttc, userdata, rc):
    """on_disconnect callback function. This function is executed when the client disconencts successfully from the broker.
    Args:
        param1 (Client): The client instance.
        param2 (str): User defined data that is defined on Client().
        param3 (dict): The response flags from the broker.
    """
    print('Client disconnected. Return code=' + str(rc))


def on_message(mqttc, userdata, msg):
    """on_message callback function. This function is executed when a message arrives (Someone published a message).
    Args:
        param1 (Client): The client instance.
        param2 (str): User defined data that is defined on Client().
        param3 (MQTTMessage): An instance of MQTTMessage, contains topic,payload,qos,retain
    """
    print('Message arrived...')
    #In the event of a message arrival, function format_message is triggered.
    format_message(msg.topic, msg.payload)


def on_subscribe(mqttc, userdata, mid, granted_qos):
    """on_subscribe callback function. This function is executed when the client subscribes successfully to a topic.
    Args:
        param1 (Client): The client instance.
        param2 (str): User defined data that is defined on Client().
        param3 (int): Mid is the message id. This id is compared with the mid that function "subscribe()" returns in order to verify the message.
        param4 (List(int)): A list of integers containing the qos for the selected subscription requests
    """
    print('subscribed (qos=' + str(granted_qos) + ')')


def on_unsubscribe(mqttc, userdata, mid, granted_qos):
    """on_unsubscribe callback function. This function is executed when the client unsubscribes successfully from a topic.
    Args:
        param1 (Client): The client instance.
        param2 (str): User defined data that is defined on Client().
        param3 (int): Mid is the message id. This id is compared with the mid that function "subscribe()" returns in order to verify the message.
        param4 (List(int)): A list of integers containing the qos for the selected subscription requests
    """
    print('unsubscribed (qos=' + str(granted_qos) + ')')


def format_message(topic, message):
    """format_message function. This function is used in order to form the message into a valid JSON record.
    Args:
        param1 (str): Topic accuired from the mqtt message
        param2 (str): message content
    """

    #String selections and reductions are performed to form the message into a JSON record
    ind = topic.find("/", 8)
    client = topic[8:ind]
    ind = message.find(",")
    rind = message.rfind(",")
    field1 = message[1:ind]
    field2 = message[ind+1:rind]
    field3 = message[rind+1:len(message)-1]

    #Get the local timestamp using functions from the time package.
    current_time = time.asctime(time.localtime(time.time()))

    #Printing the final values for debugging purposes
    print('Timestamp: ') + current_time
    print('Client Name: ') + client
    print('Topic Name: ') + topic
    print('Message: ') + message

    #This is the final String that is going to be inserted into the database JSON file.
    record = '{"timestamp":"' + current_time + '", "client":"' + client + '", "topic":"' + topic + '","field1":"' + field1 + '","field2":"' + field2 + '","field3":"' + field3 + '"}'

    #Call the database connection function (from the module "database_handler") to get access to the database and insert the data using only the record as a parameter.
    db.connect_db(record)

# We create an instacnce of an object of the mqtt.Client class. We pass the string client-1 as a client name for the constructor.
mqttc = mqtt.Client("client-1")
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.on_subscribe = on_subscribe
mqttc.on_unsubscribe = on_unsubscribe
# We set the username and password that will be user for the connection to the broker.
mqttc.username_pw_set("IoT_thesis", password="1234#2017")
try:
    #connection to the broker using ip address and port
    mqttc.connect("195.251.166.202", port=1883)
except:
    #if the connection fails...
    print("Connection failed.")
#loop function that is used in order to keep the client connected.
mqttc.loop_forever()
