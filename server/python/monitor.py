"""
    File name: monitor.py
    Author: Georgios Vrettos
    Date created: 02/11/2017
    Date last modified: 06/11/2017
    Python Version: 2.7


Example:
	$ python monitor.py
	
Todo :
	* Handling disconnects and add more functionalities to the program 

"""
from mqtt_handler import MqttHandler
from database_handler import DbHandler
# --------------------------------------------------------------------------------------------------

#Object instantiations for the Mqtt and Database classes.
mqtt = MqttHandler()
db = DbHandler()
#Calling the funcition mqtt_connect to initiate the connection to the broker.
mqtt.mqtt_connect()

#Infinite loop. This loop repeats itself every time a new message is received.
while True:

    #Call of mqtt_loop, a method that is used for the network looping porcess.
    mqtt.mqtt_loop()
    #This variable saves the latest message that is received.
    received_message = mqtt.message
    #The message is then converted to a JSON string.
    received_record = mqtt.format_message(received_message.topic,received_message.payload)
    #Call of the connect_db function for database connection.
    db.connect_db(received_record)


