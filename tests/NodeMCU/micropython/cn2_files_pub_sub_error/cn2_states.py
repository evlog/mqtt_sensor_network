"""
    File name: cn2_states.py
    Author: Georgios Vrettos
    Date created: 6/1/2018
    Date last modified: 8/1/2018
    Micropython Version: 1.9.3


This module contains the client funcitons for connection and message handling.

Todo :
	* 

"""

import gc
gc.collect()
from state import State
from cn2_mqtt import Cn2Mqtt


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
    # Object instantiations for the MQTTClient class.
    mqtt = Cn2Mqtt()

    def __init__(self):
        """ __init__ function. This is the constructor of the current state.
        """
        print('Current State: ' + str(self))

        # node_config variable, stores CN's XML in str form.
        gc.collect()
        node_config = self.read_config()
        # Client introducion to Server. The state of the object changes
        # according to SN's response.
        gc.collect()
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
        # Calling the funcition mqtt_connect to initiate the connection to the broker.
        gc.collect()
        self.mqtt.connect()
        gc.collect()
        # After connection, the client node must publish it's XML file to a specific topic.
        self.initial_connections(xml_config=xml_config)
        print("Memory Left:")
        print(gc.mem_free())
        return BlockedMode()

    def initial_connections(self,xml_config):
        """initial_connections function. In this function, the program acquires data from the XML
        and forms the first publishing topic.

        Args:
            param1 (str): The node_configuration in str form.
        """

        print("Memory Before Extraction:")
        print(gc.mem_free())
        # We extract the necessary data from the XML file using our custom element extraction function.
        networkName = self.find_xml_element(xml_string=xml_config, element="<networkName>")
        ID = self.find_xml_element(xml_string=xml_config, element="<ID>")
        country = self.find_xml_element(xml_string=xml_config, element="<country>")
        districtState = self.find_xml_element(xml_string=xml_config, element="<districtState>")
        city = self.find_xml_element(xml_string=xml_config, element="<city>")
        #gc.collect()
        areaDescription = self.find_xml_element(xml_config, "<areaDescription>")
        area = self.find_xml_element(xml_config, "<area>")
        building = self.find_xml_element(xml_config, "<building>")
        room = self.find_xml_element(xml_config, "<room>")


        # The extracted data forms the final control topic.
        client_control_topic = networkName + "/" + ID + "/" + country + "/" + districtState + "/" +\
        city + "/" + areaDescription + "/" + area + "/" + building + "/" + room + "/control";

        print (client_control_topic)
        # The Client publishes it's XML file to a specific topic using the "PUB_CONFIG_FILE" as a header str.
        self.mqtt.publish(topic=client_control_topic, msg="PUB_CONFIG_FILE, " + xml_config + ",parameter2, parameter3",retain=False, qos=1)

        # The Client subscribes to the same topic in order to get the server response.
        self.mqtt.subscribe(topic=client_control_topic, qos=1)


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

        gc.collect()
        print("Memory in Blocked Mode:")
        print(gc.mem_free())


class ActiveMode(State):
    """
    This state is used when client is successfully validated.
    The device changes state to active to initalize it's basic functions.
    """

    def __init__(self):
        """ __init__ function. This is the constructor of the current state.
        """
        print('Current State: ' + str(self))

