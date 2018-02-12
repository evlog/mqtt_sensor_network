"""
    File name: cn2_states.py
    Author: Georgios Vrettos
    Date created: 6/1/2018
    Date last modified: 10/1/2018
    Micropython Version: 1.9.3


This module contains the client funcitons for connection and message handling.

Todo :
	* 

"""

import gc
gc.collect()
from state import State
from cn2_mqtt import Cn2Mqtt
from micropython import const
from sensors import Sensors
import time


# Global variables
# --------------------------------------------------------------------------------------------------
XML_FILE_PATH = "/cn2_config.xml"


# --------------------------------------------------------------------------------------------------

class InitialMode(State):
    """
    This state is used as default before client validation.
    In this mode, the cliend sends it's xml file to the SN for validation.
    If the node is valid, the program's state changes to ActiveMode.
    """

    # Class functionality variables.

    def __init__(self):
        """ __init__ function. This is the constructor of the current state.
        """
        print('Current State: ' + str(self))

        # node_config variable, stores CN's XML in str form.
        node_config = self.read_config()

        # Client introducion to Server. The state of the object changes
        # according to SN's response.
        self.state = self.client_introduce(xml_config=node_config)



    def read_config(self):
        """read_config function. This function is used to convert the XML config file to string.
        """
        xml_file = open(XML_FILE_PATH, 'r')
        xml_config_str = xml_file.read()
        xml_file.close()
        return xml_config_str

    def client_introduce(self, xml_config):
        """client_introduce function. This function is used for the initial introduction
         of the Client to the Server Node.

        Args:
            param1 (str): The node_configuration in str form.
        """
        # Object instantiations for the MQTTClient class.
        mqtt = Cn2Mqtt()

        # Calling the funcition mqtt_connect to initiate the connection to the broker.
        mqtt.connect()
        # After connection, the client node must publish it's XML file to a specific topic.
        config_list = self.initial_connections(mqtt=mqtt,xml_config=xml_config)

        # Infinite loop. The program stands by for any incomming message.
        while True:
            # Call of standby_loop, to set the program waiting for a new message.
            mqtt.standby_loop()

            if (mqtt.r_message.find("SET_CN_MODE, active") != -1):
                # If the received message contains the phrase above, the client enters active mode.
                # The current state passes the mqtt connection object and the list to the next state.
                return ActiveMode(mqtt=mqtt,config_list=config_list)
            elif (mqtt.r_message.find("SET_CN_MODE, blocked") != -1):
                # If the received message contains the phrase above, the client enters blocked mode.
                # Closing the connection between the invalid node and the broker
                mqtt.disconnect()
                return BlockedMode()


    def initial_connections(self,mqtt,xml_config):
        """initial_connections function. In this function, the program acquires data from the XML
        and forms the first publishing topic. In the end it returns some extracted XML data in a list.

        Args:
            param1 (Cn2Mqtt): The mqtt object instance
            param2 (str): The node_configuration in str form.

        """
        # We extract the necessary data from the XML file using our custom element extraction function.
        networkName = self.find_xml_element(xml_string=xml_config, element="<networkName>")
        serverID = self.find_xml_element(xml_config, "<serverID>")
        ID = self.find_xml_element(xml_string=xml_config, element="<ID>")
        country = self.find_xml_element(xml_string=xml_config, element="<country>")
        districtState = self.find_xml_element(xml_string=xml_config, element="<districtState>")
        city = self.find_xml_element(xml_string=xml_config, element="<city>")
        areaDescription = self.find_xml_element(xml_config, "<areaDescription>")
        area = self.find_xml_element(xml_config, "<area>")
        building = self.find_xml_element(xml_config, "<building>")
        room = self.find_xml_element(xml_config, "<room>")
        client_extra_topic = self.find_xml_element(xml_config,"<topicName>")

        # Extracred data are saved in a list for later use
        config_list = [networkName,serverID,ID,country,districtState,city,areaDescription,area,
                       building,room,client_extra_topic]

        # The extracted data forms the final control topic.
        client_control_topic = networkName + "/" + ID + "/" + country + "/" + districtState + "/" +\
        city + "/" + areaDescription + "/" + area + "/" + building + "/" + room + "/control";

        print("Memory before publish:")
        print(gc.mem_free())
        # The Client publishes it's XML file to a specific topic using the "PUB_CONFIG_FILE" as a header str.
        mqtt.publish(topic=client_control_topic, msg="PUB_CONFIG_FILE, " +
        xml_config + ",parameter2, parameter3",retain=False, qos=1)

        print("Memory before subscribe:")
        print(gc.mem_free())
        # The Client subscribes to the same topic in order to get the server response.
        mqtt.subscribe(topic=client_control_topic, qos=1)

        # The function returns the extracted content list
        return config_list


    def find_xml_element(self, xml_string, element):
        """find_xml_element function. This function is used to extract data
        from the XML file.

        Args:
            param1 (str): The node_configuration in str form.
            param2 (str): The element and search pattern.
        """
        # The starting posision of the content
        start = xml_string.find(element)
        # The ending character.
        end = xml_string.find('<', start + 1)
        # The result of our search is the word/phrase between start and end - the search pattern.
        result = xml_string[start + len(element):end]
        return result



class BlockedMode(State):
    """
    The blocked state describes the device as unauthenticated. 
    """

    def __init__(self):
        """ __init__ function. This is the constructor of the current state.
        """
        print('Current State: ' + str(self))
        print("Disconnect everything and do a hard reset")

        #gc.collect()
        #print("Memory in Blocked Mode:")
        #print(gc.mem_free())



class ActiveMode(State):
    """
    This state is used when client is successfully validated.
    The device changes state to active to initalize it's basic functions.
    """

    def __init__(self,mqtt,config_list):
        """ __init__ function. This is the constructor of the current state.
        Args:
            param1 (Cn2Mqtt): The mqtt object instance
            param1 (list): A list containing extracted data from the XML

        """
        print('Current State: ' + str(self))

        gc.collect()
        print("Memory in Active Mode:")
        print(gc.mem_free())

        # The mqtt connection object is passed through the constructor form the previous state.
        self.mqtt = mqtt

        # The function that initates the loop of the program.
        self.mqtt_client(self.mqtt,config_list)


    def mqtt_client(self,mqtt,config_list):
        """mqtt_client function. This function includes the main looping for incoming messages.
        Args:
            param1 (Cn2Mqtt): The mqtt object instance
            param1 (list): A list containing extracted data from the XML

        """
        # After entering active mode, the client subscribes to the necessary topics.
        #self.active_connections(mqtt,config_list)
        #gc.collect()
        #print("Memory after all subscriptions:")
        #print(gc.mem_free())

        # Infinite loop. The program stands by for any incomming message.
        while True:
            gc.collect()
            # Call of standby_loop, to set the program waiting for a new message.
            # mqtt.standby_loop()
            #print(mqtt.r_topic + ": " + mqtt.r_message)
            measurements = Sensors()
            measurements.get_fire_status()
            time.sleep(0.05)
            measurements.get_temp_hum_status()
            time.sleep(10)


    def active_connections(self,mqtt,config_list):
        """active_connections function. In this function, the program acquires data from the XML
        forms and subscribes to all necessary topics.

        Args:
            param1 (Cn1Mqtt): The mqtt connection object.
            param1 (list): A list containing extracted data from the XML
        """

        # Construction the topic. List indexes are fixed and do not change.
        items = config_list[0] + "/" + config_list[1] + "/" + config_list[3] +\
        "/" + config_list[4] + "/" + config_list[5] + "/" + config_list[6] + "/" + config_list[7] + "/" +\
        config_list[8] + "/" + config_list[9]

        # The client subscribes to local time and server status topic.
        sys_local_time_topic = "$SYS/" + items + "/localDateTime";
        sys_server_status_topic = "$SYS/" + items + "/" + config_list[1] + "/status";

        mqtt.subscribe(topic=sys_local_time_topic, qos=1)
        mqtt.subscribe(topic=sys_server_status_topic, qos=1)

        # If there is an extra subscription topic inside the client's XML file, the client subscribes to it.
        if(config_list[10] != ""):
            mqtt.subscribe(topic=config_list[9], qos=1)

        print("Memory Left:")
        print(gc.mem_free())










