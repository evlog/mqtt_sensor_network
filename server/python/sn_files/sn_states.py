"""
    File name: sn_states.py
    Author: Georgios Vrettos
    Date created: 11/12/2017
    Date last modified: 17/12/2017
    Python Version: 2.7

This module contains the server funcitons for connection and message handling.
In this module, functions from the package "xmltodict" are used. 
To install the package using pip issue the following command:
$pip install xmltodict 

Todo :
	* 

"""

from state import State
from validate_xml import XmlValidator
from sn_mqtt import SnMqtt
import xmltodict
from json import dumps
from sn_db import Sn_db
import datetime
import time



# Global variables
# --------------------------------------------------------------------------------------------------
XML_FILE_PATH = "/home/vrettel/Dropbox/Thesis/Code/PC Server/sn_files/sn_config.xml"

# --------------------------------------------------------------------------------------------------

class ActiveMode(State):
    """
    This state is used as default for the server node. On this state the server program executes
    it's basic functions.
    """

    # Class functionality variables.
    # server configuration file in str form.
    server_config_str = ""

    def __init__(self):
        """ __init__ function. This is the constructor of the current state.
        """
        print('Current State: ' + str(self))
        # This function handles the server setup before connecting to mqtt network.
        self.initial_setup()
        # This function is used to connect to mqtt and handle messages.
        self.mqtt_server()


    def on_event(self, event):
        """on_event function. This function changes the client state on demand.
        Args:
            param1 (str): The target state.
        """
        if event == 'blocked':
            return BlockedMode()

        return self


    def initial_setup(self):
        """initial_setup function. This function is used for the initial setup of
        the server node.
        """
        # the server configuration file in str form.
        self.server_config_str = self.read_config()
        # the SN performs validation of it's own xml file
        if(self.validate_config_file(self.server_config_str)==False):
            # If the file is not valid print message.
            print('Check Server configuration file')
        else:
            print('Server Configuration OK')
            # Convert XML str to JSON str.
            server_config_json = self.xml_to_json(self.server_config_str)
            # Insert/Update node_configuration on database
            db = Sn_db()
            db.connect_db()
            # Upsert function Inserts or Updates the nodes table if the node already exists.
            db.upsert_node_db(server_config_json, self.get_local_time())
            db.disconnect_db()


    def read_config(self):
        """read_config function. This function is used to convert the XML config file to string.
        """

        xml_file = open(XML_FILE_PATH, 'r')
        xml_config_str = xml_file.read()
        xml_file.close()
        return xml_config_str

    def validate_config_file(self,xml_config_str):
        """validate_config_file function. This function validates an XML against an xml schema.
        Args:
            param1 (str): The xml configuration string.
        """
        val = XmlValidator()
        # the function returns True if the file is valid or False otherwise.
        return val.xml_validator(xml_config_str)

    def mqtt_server(self):
        """mqtt_server function. This function creates an mqtt connection object and starts
        the connection to the network. It also handles all the incomming traffic accordingly.

        """
        # Object instantiations for the Mqtt Client class.
        mqtt = SnMqtt()
        # Calling the funcition mqtt_connect to initiate the connection to the broker.
        mqtt.mqtt_connect()

        # Inital topic subscriotions.
        self.initial_connections(mqtt,self.server_config_str)

        # Infinite loop. This loop repeats itself every time a new message is received.
        flag = True
        while flag:
            # Call of mqtt_loop, a method that is used for the network looping porcess.
            mqtt.mqtt_loop()
            # This variable saves the latest message that is received.
            received_message = mqtt.message
            #print(received_message.topic + ": " + received_message.payload)
            self.handle_message(mqtt,received_message.topic,received_message.payload)




    def handle_message(self,mqtt, topic, payload):
        """handle_message function. This function handles all incomming traffic.
        Args:
            param1 (SnMqtt): The mqtt connection instance.
            param2 (str): The topic of the incomming message.
            param3 (str): The payload of the incomming message.

        """
        if(payload.rfind("PUB_CONFIG_FILE")!=-1):
            # If the message's payload contains this pattern,
            # the message contains an XML file for the new client node.
            xml_start = payload.find('<?xml version="1.0"?>')
            xml_end = payload.rfind('</nodeConfiguration>')

            if(xml_start!=-1 and xml_end!=-1):
                # if the string is an xml file
                # string trimming is performed to discard uncesessary data.
                client_config_str = payload[xml_start:xml_end + len('</nodeConfiguration>')]
                # if the incomming xml file is valid (through xml validation function)
                if(self.validate_config_file(client_config_str)):
                    print("Client node valid.")
                    # the SN publishes to the same topic a set_node_mode active command.
                    mqtt.publish(topic=topic,payload="SET_CN_MODE, active,"
                    " parameter2, parameter3", qos=1, retain=False)
                    # Convert the XML file to JSON
                    client_config_json = self.xml_to_json(client_config_str)
                    # Insert/Update node_configuration on database
                    db = Sn_db()
                    db.connect_db()
                    # Upsert function Inserts or Updates the nodes table if the node already exists.
                    db.upsert_node_db(client_config_json,self.get_local_time())
                    time.sleep(1)
                    # After databases update, the SN publishes messages to $SYS topics.
                    self.active_connections(mqtt,self.server_config_str,client_config_str,db)
                    # Database connection ends.
                    db.disconnect_db()
                else:
                    # if the incomming xml file is invalid (through xml validation function)
                    print("Client node invalid.")
                    # the SN publishes to the same topic a set_node_mode blocked command.
                    mqtt.publish(topic=topic, payload="SET_CN_MODE, blocked,"
                    " parameter2, parameter3", qos=1, retain=False)

            else:
                # if the string is not an xml file
                print("Client node invalid.")
                # the SN publishes to the same topic a set_node_mode blocked command.
                mqtt.publish(topic=topic, payload="SET_CN_MODE, blocked,"
                " parameter2, parameter3", qos=1, retain=False)
        else:
            # other kind of messages are ignored for the time being.
            pass

    def xml_to_json(self,xml_str):
        """xml_to_json function. This function converts XML str to JSON str.
        Args:
            param1 (str): xml string.

        """
        # Parses xml to dictionary and then converts to JSON.
        return dumps(xmltodict.parse(xml_str))

    def get_local_time(self):
        """get_local_time function. This function returns the local time.
        """
        # Get the local timestamp using functions from the datetime package.
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return current_time


    def initial_connections(self,mqtt,xml_config):
        """initial_connections function. In this function, 
        the program acquires data from the server XML
        and forms the first subscribing topic.

        Args:
            param1 (SnMqtt): The mqtt connection instance.
            param2 (str): The node_configuration in str form.

        """

        # We extract the necessary data from the XML file using our custom element extraction function.
        networkName = self.find_xml_element(xml_config,"<networkName>")
        country = self.find_xml_element(xml_config, "<country>")
        districtState = self.find_xml_element(xml_config, "<districtState>")
        city = self.find_xml_element(xml_config, "<city>")
        areaDescription = self.find_xml_element(xml_config, "<areaDescription>")
        area = self.find_xml_element(xml_config, "<area>")
        building = self.find_xml_element(xml_config, "<building>")
        room = self.find_xml_element(xml_config, "<room>")

        # The extracted data forms the final control topic.
        client_control_topic = networkName + "/+/" + country + "/" + districtState + "/" +\
        city + "/" + areaDescription + "/" + area + "/" + building + "/" + room + "/control";
        #print (client_control_topic)
        # The SN subscribes to the client control topic and waits for incomming client
        # configuration files.
        mqtt.subscribe(topic=client_control_topic, qos=1)



    def active_connections(self,mqtt,server_xml_config,client_xml_config,db_connection):
        """active_connections function. In this function, 
        the program acquires data from the XML files,
        forms and publishes to all necessary  $SYS topics.

        Args:
            param1 (Cn1Mqtt): The mqtt connection object.
            param2 (str): The server configuration string.
            param3 (str): The client configuration string.
            param4 (Sn_db): The database connection instance.

        """
        # We extract the necessary data from the server XML file using our custom element extraction function.
        networkName = self.find_xml_element(server_xml_config,"<networkName>")
        serverID = self.find_xml_element(server_xml_config, "<serverID>")
        country = self.find_xml_element(server_xml_config, "<country>")
        districtState = self.find_xml_element(server_xml_config, "<districtState>")
        city = self.find_xml_element(server_xml_config, "<city>")
        areaDescription = self.find_xml_element(server_xml_config, "<areaDescription>")
        area = self.find_xml_element(server_xml_config, "<area>")
        building = self.find_xml_element(server_xml_config, "<building>")
        room = self.find_xml_element(server_xml_config, "<room>")
        serverIP = self.find_xml_element(server_xml_config, "<IPAddress>")

        # The server forms the $SYS topics using Server's xml file data.
        sys_local_time_topic = "$SYS/" + networkName + "/" + serverID + "/" + country\
                               + "/" + districtState + "/" + city + "/" + areaDescription\
                               + "/" + area + "/" + building + "/" + room + "/localDateTime";
        sys_server_status_topic = "$SYS/" + networkName + "/" + serverID + "/" + country\
                                  + "/" + districtState + "/" + city + "/" + areaDescription\
                                  + "/" + area + "/" + building + "/" + room + "/" + serverID + "/status";
        sys_network_status_topic = "$SYS/" + networkName + "/" + serverID + "/" + country\
                                   + "/" + districtState + "/" + city + "/" + areaDescription\
                                   + "/" + area + "/" + building + "/" + room + "/networkStatus";
        sys_server_ip_topic = "$SYS/" + networkName + "/" + serverID + "/" + country\
                              + "/" + districtState + "/" + city + "/" + areaDescription\
                              + "/" + area + "/" + building + "/" + room + "/ipAddress";
        sys_num_connected_nodes_topic = "$SYS/" + networkName + "/" + serverID + "/" + country\
                                        + "/" + districtState + "/" + city + "/" + areaDescription\
                                        + "/" + area + "/" + building + "/" + room + "/numOfConnectedNodes";


        # We extract the necessary data from the client XML file using our custom element extraction function.
        clientID = self.find_xml_element(client_xml_config, "<ID>")
        clientIP = self.find_xml_element(client_xml_config, "<IPAddress>")

        # The server forms the $SYS topics using Client's xml file data.
        sys_client_ip_topic = "$SYS/" + networkName + "/" + serverID + "/" + country\
                              + "/" + districtState + "/" + city + "/" + areaDescription\
                              + "/" + area + "/" + building + "/" + room + "/" + clientID + "/ipAddress";
        sys_client_status_topic = "$SYS/" + networkName + "/" + serverID + "/" + country\
                                  + "/" + districtState + "/" + city + "/" + areaDescription\
                                  + "/" + area + "/" + building + "/" + room + "/" + clientID + "/status";

        # SN publishes data to all $SYS topics.
        mqtt.publish(topic=sys_network_status_topic, payload="active", qos=1, retain=False)
        time.sleep(0.2)
        mqtt.publish(topic=sys_local_time_topic, payload=self.get_local_time(), qos=1, retain=False)
        time.sleep(1)
        mqtt.publish(topic=sys_server_ip_topic, payload=serverIP, qos=1, retain=False)
        time.sleep(0.2)
        mqtt.publish(topic=sys_server_status_topic, payload="active", qos=1, retain=False)
        time.sleep(0.2)
        mqtt.publish(topic=sys_client_ip_topic, payload=clientIP, qos=1, retain=False)
        time.sleep(0.2)
        mqtt.publish(topic=sys_client_status_topic,
                     payload=db_connection.get_node_status(clientID), qos=1, retain=False)
        time.sleep(0.2)
        mqtt.publish(topic=sys_num_connected_nodes_topic,
                     payload=db_connection.get_active_nodes_count(), qos=1, retain=False)


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
    The blocked state renders the device blocked. 
    """
    def __init__(self):
        """ __init__ function. This is the constructor of the current state.
        """
        print('Current State: ' + str(self))
        self.block()

    def on_event(self,event):
        """on_event function. This function changes the server state on demand.
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



