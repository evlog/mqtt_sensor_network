"""
    File name: sn_states.py
    Author: Georgios Vrettos
    Date created: 11/12/2017
    Date last modified: 18/4/2018
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
from sn_thread import Sn_thread




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
    # the mqtt object
    mqtt = None
    # a list that contains all the nodes that publish messages of any kind.
    connected_nodes = []
    # a list that works as a message buffer.
    msg_buffer = []

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
        self.mqtt = SnMqtt()
        # Calling the funcition mqtt_connect to initiate the connection to the broker.
        self.mqtt.mqtt_connect()

        # Inital topic subscriotions.
        self.initial_connections(self.mqtt,self.server_config_str)

        # A thread object for a parallel buffer checking function
        buffer_thread = Sn_thread(id = "buffer",callback=self.check_buffer)
        # The thread starts
        buffer_thread.start()

        # Infinite loop for the MQTT looping process.
        while True:
            # Call of mqtt_loop, a method that is used for the network looping process.
            self.mqtt.mqtt_loop()


    def check_buffer(self,id,data):
        """check_buffer function. This function implements a loop that
        checks the buffer periodically for incoming messages. Content from the main buffer
        is moved to a temporary buffer for further processing.
        Args:
            param1 (str): Thread id.
            param2 (list): list containing useful data.

        """

        while(True):
            #time.sleep(35)
            self.msg_buffer = []
            current_length = len(self.mqtt.buffer)
            i=0
            # Messages from the main buffer are moved to the temporary buffer.
            while( i < current_length):
                self.msg_buffer.append(self.mqtt.buffer[i])
                self.mqtt.buffer.pop(i)
                current_length-=1

            # The content of the temporary buffer is handled for porcessing.
            self.handle_message(self.mqtt, self.msg_buffer)





    def handle_message(self,mqtt, msg_buffer):
        """handle_message function. This function handles all incomming traffic.
        Args:
            param1 (SnMqtt): The mqtt connection instance.
            param2 (list): A list of messages from the temporary buffer.

        """

        for msg in msg_buffer:
            # For every message in the temporary buffer
            topic = msg.topic
            payload = msg.payload
            if(topic.rfind("control")!=-1):
                # If the topic is a control topic
                if(payload.find("PUB_CONFIG_FILE")!=-1):
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

                            # Initiating connection with the database.
                            db = Sn_db()
                            db.connect_db()

                            # This is the last known severity mode of the current node in the database.
                            # The mode is retrieved using the node id. The id is extracted from the topic.
                            last_known_mode = db.get_node_sev_mode(self.find_in_topic(topic,2))

                            # the SN publishes to the same topic a set_node_mode active command and severity mode.
                            mqtt.publish(topic=topic, payload="SET_CN_FUNCTIONAL_MODE, active," +
                                                last_known_mode + ", parameter2, parameter3", qos=1, retain=False)
                            # Convert the XML file to JSON
                            client_config_json = self.xml_to_json(client_config_str)

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
                            mqtt.publish(topic=topic, payload="SET_CN_FUNCTIONAL_MODE, blocked,"
                            " parameter2, parameter3", qos=1, retain=False)

                    else:
                        # if the string is not an xml file
                        print("Client node invalid.")
                        # the SN publishes to the same topic a set_node_mode blocked command.
                        mqtt.publish(topic=topic, payload="SET_CN_FUNCTIONAL_MODE, blocked,"
                        " parameter2, parameter3", qos=1, retain=False)

                elif(payload.find("PUB_CN_SEVERITY_MODE")!=-1):
                    # if the topic is refers to severity mode change

                    sev_mode = self.find_sev_mode(payload)
                    node_id = self.find_in_topic(topic,2)

                    db = Sn_db()
                    db.connect_db()
                    # Update column function updates the severity mode of the current node.
                    db.update_node_column("sev_mode",sev_mode,node_id)
                    db.disconnect_db()

                else:
                    # other kind of control messages are being ignored for now.
                    pass


            elif(topic.rfind("Sensor")!=-1):
                # if the topic of a message contains the word Sensor
                # another thread is executed to process the data and save it into the DB
                db_thread = Sn_thread(self.find_in_topic(topic,2),msg,self.save_sensor_data)
                db_thread.start()




    def save_sensor_data(self,node_id,data_msg):
        """save_sensor_data function. This function saves the sensor data from a message
        to the database.
        Args:
            param1 (str): The node id.
            param2 (list): A data message.

        """

        # the data table is processed for content extraction
        # the process returns a dictionary object.
        data = self.find_data_values(data_msg)
        # Initiating connection with the database.
        db = Sn_db()
        db.connect_db()
        # Depending on the message topic,
        # the data is being inserted to a specific table in the database.
        if(data_msg.topic.rfind("Temperature")!=-1):
            db.insert_client_data(node_id, "temperature", data)
            db.disconnect_db()

        elif(data_msg.topic.rfind("Humidity")!=-1):
            db.insert_client_data(node_id, "humidity", data)
            db.disconnect_db()

        elif(data_msg.topic.rfind("Flame")!=-1):
            db.insert_client_data(node_id, "flame", data)
            db.disconnect_db()




    def find_data_values(self,msg):
        """find_data_values function. This function extracts the data from every message
        in the list, and it returns a key:value dictionary.
        Args:
            param1 (list): A list of messages from a specific client.

        """

        # The dictionary is initialized with default values.
        #extracted_data = {'temperature_type': 'F', 'temperature_range': 'F', 'temperature': '-1',
        #                  'humidity_type': 'F', 'humidity': '-1', 'humidity_range': 'F',
        #                  'flame_type': 'F', 'flame': '-1', 'flame_range': 'F'}

            # for every message in the list data extraction is performed.
        extracted_data = {}

        if(msg.topic.rfind("Temperature")!=-1):
                extracted_data['temperature_type'] = self.find_in_payload(msg.payload, 1)
                extracted_data['temperature_range'] = self.find_in_payload(msg.payload, 2)
                extracted_data['temperature'] = self.find_in_payload(msg.payload,3)
        elif(msg.topic.rfind("Humidity")!=-1):
                extracted_data['humidity_type'] = self.find_in_payload(msg.payload, 1)
                extracted_data['humidity_range'] = self.find_in_payload(msg.payload, 2)
                extracted_data['humidity'] = self.find_in_payload(msg.payload,3)
        elif(msg.topic.rfind("Flame")!=-1):
                extracted_data['flame_type'] = self.find_in_payload(msg.payload, 1)
                extracted_data['flame_range'] = self.find_in_payload(msg.payload, 2)
                extracted_data['flame'] = self.find_in_payload(msg.payload,3)


        return extracted_data


    def find_sev_mode(self,payload):
        """find_sev_mode function. This function extracts the severity mode
        from an incoming message.
        Args:
            param1 (str): Message payload.

        """
        # A severity mode update message has a very specific format that makes it easier to extract data.
        start = payload.find(",") + 2
        end = payload.rfind("Mode") + len("Mode")
        return  payload[start:end]

    def find_in_payload(self,payload,position):
        """find_in_topic function. This function extracts a specific item from a data message
        depending on the position of the item.
        Args:
            param1 (str): Message payload.
            param1 (str): Word position on topic.

        """

        # Word extraction from the current topic.
        i=1
        start = 0
        end = payload.find(',')
        # Depending on the position of the item that we need to extract from the topic
        # the loop runs to locate the item between two "/".
        while i < position:
            start = end + 1
            if(payload.find(',',end + 1)!=-1):
                end = payload.find(',',end + 1)
            else:
                end = len(payload)
            i = i + 1
        # when the desired word indexes are found we extract the final item.
        return payload[start:end]


    def find_in_topic(self,topic,position):
        """find_in_topic function. This function extracts a specific item from a topic
        depending on the position of the item.
        Args:
            param1 (str): Message topic.
            param1 (str): Word position on topic.

        """

        # Word extraction from the current topic.
        i=1
        start = 0
        end = topic.find('/')
        # Depending on the position of the item that we need to extract from the topic
        # the loop runs to locate the item between two "/".
        while i < position:
            start = end + 1
            if(topic.find('/',end + 1)!=-1):
                end = topic.find('/',end + 1)
            else:
                end = len(topic)
            i = i + 1
        # when the desired word indexes are found we extract the final item.
        return topic[start:end]


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

        # The extracted data forms the final sensor data topic.
        sensor_data_topic = networkName + "/+/" + country + "/" + districtState + "/" +\
        city + "/" + areaDescription + "/" + area + "/" + building + "/" + room + "/+";

        # The SN subscribes to the client control and sensor data topics and waits for incomming client
        # configuration files or sensor data.
        mqtt.subscribe(topic=client_control_topic, qos=1)
        mqtt.subscribe(topic=sensor_data_topic, qos=1)

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



