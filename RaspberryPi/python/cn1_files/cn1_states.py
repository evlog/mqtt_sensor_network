"""
    File name: cn1_states.py
    Author: Georgios Vrettos
    Date created: 10/12/2017
    Date last modified: 16/12/2017
    Python Version: 2.7


This module contains the client funcitons for connection and message handling.

Todo :
	* 

"""

from state import State
from cn1_mqtt import Cn1Mqtt

# Global variables
# --------------------------------------------------------------------------------------------------
XML_FILE_PATH = "/home/vrettel/Dropbox/Thesis/Code/RaspberryPi/cn1_files/cn1_config.xml"

# --------------------------------------------------------------------------------------------------

class InitialMode(State):
    """
    This state is used as default before client validation.
    In this mode, the cliend sends it's xml file to the SN for validation.
    If the node is valid, the program's state changes to ActiveMode.
    """

    # Class functionality variables.
    # Object instantiations for the Mqtt Client class.
    mqtt = Cn1Mqtt()

    def __init__(self):
        """ __init__ function. This is the constructor of the current state.
        """
        print('Current State: ' + str(self))

        # node_config variable, stores CN's XML in str form.
        node_config = self.read_config()
        # Client introducion to Server. The state of the object changes
        # according to SN's response.
        self.state = self.client_introduce(xml_config=node_config)

    '''def on_event(self, event):
        """

        """
        # When in initial mode do something...

        if event == 'active':
            return ActiveMode()
        elif event =='blocked':
            return BlockedMode()

        return self
    '''

    def read_config(self):
        """read_config function. This function is used to convert the XML config file to string.
        """

        xml_file = open(XML_FILE_PATH, 'r')
        xml_config_str = xml_file.read()
        xml_file.close()
        return xml_config_str



    def client_introduce(self,xml_config):
        """client_introduce function. This function is used for the initial introduction
         of the Client to the Server Node.
        
        Args:
            param1 (str): The node_configuration in str form.
        """
        # Calling the funcition mqtt_connect to initiate the connection to the broker.
        self.mqtt.mqtt_connect()

        # After connection, the client node must publish it's XML file to a specific topic.
        self.initial_connections(xml_config)

        # Infinite loop. This loop repeats itself every time a new message is received.
        flag = True
        while flag:
            # Call of mqtt_loop, a method that is used for the network looping porcess.
            self.mqtt.mqtt_loop()
            flag = False
            print(self.mqtt.message.topic + ": " + self.mqtt.message.payload)

        if (self.mqtt.message.payload.find("SET_CN_MODE, active") != -1):
            # If the received message contains the phrase above, the client enters active mode.
            # The current state passes the mqtt connection object to the next state.
            return ActiveMode(self.mqtt)
        elif (self.mqtt.message.payload.find("SET_CN_MODE, blocked") != -1):
            # If the received message contains the phrase above, the client enters blocked mode.
            # Closing the connection between the invalid node and the broker
            self.mqtt.disconnect()
            return BlockedMode()

    def initial_connections(self,xml_config):
        """initial_connections function. In this function, the program acquires data from the XML
        and forms the first publishing topic.

        Args:
            param1 (str): The node_configuration in str form.
        """

        # We extract the necessary data from the XML file using our custom element extraction function.
        networkName = self.find_xml_element(xml_config,"<networkName>")
        ID = self.find_xml_element(xml_config, "<ID>")
        country = self.find_xml_element(xml_config, "<country>")
        districtState = self.find_xml_element(xml_config, "<districtState>")
        city = self.find_xml_element(xml_config, "<city>")
        areaDescription = self.find_xml_element(xml_config, "<areaDescription>")
        area = self.find_xml_element(xml_config, "<area>")
        building = self.find_xml_element(xml_config, "<building>")
        room = self.find_xml_element(xml_config, "<room>")

        # The extracted data forms the final control topic.
        client_control_topic = networkName + "/" + ID + "/" + country + "/" + districtState + "/" +\
        city + "/" + areaDescription + "/" + area + "/" + building + "/" + room + "/control";

        #print (client_control_topic)
        # The Client publishes it's XML file to a specific topic using the "PUB_CONFIG_FILE" as a header str.
        self.mqtt.publish(topic=client_control_topic, payload="PUB_CONFIG_FILE, " +
        xml_config + ",parameter2, parameter3", qos=1, retain=False)

        # The Client subscribes to the same topic in order to get the server response.
        self.mqtt.subscribe(topic=client_control_topic, qos=1)



    def find_xml_element(self,xml_string,element):
        """find_xml_element function. This function is used to extract data
        from the XML file.

        Args:
            param1 (str): The node_configuration in str form.
            param2 (str): The element and search pattern.
        """
        # The starting posision of the content
        start = xml_string.find(element)
        # The ending character.
        end = xml_string.find('<',start + 1)
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
        self.block()

    def on_event(self,event):
        """on_event function. This function changes the client state on demand.
        Args:
            param1 (str): The target state.
        """
        if event == 'active':
            return ActiveMode()

        return self

    def block(self):
        """block function. This function will include any action 
        concerning blocked mode
        """

        print("Disconnect everything and do a hard reset")



class ActiveMode(State):
    """
    This state is used when client is successfully validated.
    The device changes state to active to initalize it's basic functions.
    """


    def __init__(self,mqtt):
        """ __init__ function. This is the constructor of the current state.
        """
        print('Current State: ' + str(self))
        # The mqtt connection object is passed through the constructor form the previous state.
        self.mqtt = mqtt

        # The node configuration XML string.
        node_config = self.read_config()
        # The function that initates the loop of the program.
        self.mqtt_client(self.mqtt,node_config)


    def mqtt_client(self,mqtt,xml_config):
        """mqtt_client function. This function includes the main looping for incoming messages.
        Args:
            param1 (str): The mqtt connection object.
            param1 (str): The xml configuration string.

        """
        # After entering active mode, the client subscribes to the necessart topics.
        self.active_connections(mqtt,xml_config)

        # Infinite loop. This loop repeats itself every time a new message is received.
        flag = True
        while flag:
            # Call of mqtt_loop, a method that is used for the network looping porcess.
            mqtt.mqtt_loop()
            # This variable saves the latest message that is received.
            received_message = mqtt.message
            print(received_message.topic + ": " + received_message.payload)



    def read_config(self):
        """read_config function. This function is used to convert the XML config file to string.
        """

        xml_file = open(XML_FILE_PATH, 'r')
        xml_config_str = xml_file.read()
        xml_file.close()
        return xml_config_str



    def on_event(self, event):
        """on_event function. This function changes the client state on demand.
        Args:
            param1 (str): The target state.
        """
        if event == 'blocked':
            return BlockedMode()

        return self


    def active_connections(self,mqtt,xml_config):
        """active_connections function. In this function, the program acquires data from the XML
        forms and subscribes to all necessary topics.

        Args:
            param1 (Cn1Mqtt): The mqtt connection object.
            param2 (str): The node_configuration in str form.
        """

        # We extract the necessary data from the XML file using our custom element extraction function.
        networkName = self.find_xml_element(xml_config,"<networkName>")
        serverID = self.find_xml_element(xml_config, "<serverID>")
        country = self.find_xml_element(xml_config, "<country>")
        districtState = self.find_xml_element(xml_config, "<districtState>")
        city = self.find_xml_element(xml_config, "<city>")
        areaDescription = self.find_xml_element(xml_config, "<areaDescription>")
        area = self.find_xml_element(xml_config, "<area>")
        building = self.find_xml_element(xml_config, "<building>")
        room = self.find_xml_element(xml_config, "<room>")

        # The client subscribes to local time and server status topic.
        sys_local_time_topic = "$SYS/" + networkName + "/" + serverID + "/" + country + "/" + \
        districtState + "/" + city + "/" + areaDescription + "/" + area + "/" + building +\
        "/" + room + "/localDateTime";

        sys_server_status_topic = "$SYS/" + networkName + "/" + serverID + "/" + country + "/" + \
        districtState + "/" + city + "/" + areaDescription + "/" + area + "/" + building +\
        "/" + room + "/" + serverID + "/status";
        #print(sys_local_time_topic)
        #print(sys_server_status_topic)
        mqtt.subscribe(topic=sys_local_time_topic, qos=1)
        mqtt.subscribe(topic=sys_server_status_topic, qos=1)

        # If there is an extra subscription topic inside the client's XML file, the client subscribes to it.
        client_extra_topic = self.find_xml_element(xml_config,"<topicName>")
        if(client_extra_topic != ""):
            mqtt.subscribe(topic=client_extra_topic, qos=1)


    def find_xml_element(self,xml_string,element):
        """find_xml_element function. This function is used to extract data
        from the XML file.

        Args:
            param1 (str): The node_configuration in str form.
            param2 (str): The element and search pattern.
        """
        # The starting posision of the content
        start = xml_string.find(element)
        # The ending character.
        end = xml_string.find('<',start + 1)
        # The result of our search is the word/phrase between start and end - the search pattern.
        result = xml_string[start + len(element):end]
        return result

