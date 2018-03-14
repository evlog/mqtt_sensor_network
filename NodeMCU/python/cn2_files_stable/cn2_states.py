"""
    File name: cn2_states.py
    Author: Georgios Vrettos
    Date created: 6/1/2018
    Date last modified: 12/3/2018
    Micropython Version: 1.9.3


This module contains the client funcitons for connection, message handling and data processing.

Todo :
	* Improve the linear regression function for better results.

"""

import gc
gc.collect()
from state import State
from cn2_mqtt import Cn2Mqtt
from sensors import Sensors
import time
import machine
import micropython
# Initial memory allocation (in bytes) for handling exception messages during an interrupt.
micropython.alloc_emergency_exception_buf(100)

# Global variables
# --------------------------------------------------------------------------------------------------
XML_FILE_PATH = "/cn2_config.xml"

# Change rate value to be compared with the gathered data (°C/min).
TEMP_CHANGE_RATE_WARNING_THRESHOLD = 0.06
TEMP_CHANGE_RATE_DANGER_THRESHOLD = 0.1

# Ambient Temperature Thresholds (°C).
TEMP_WARNING_THRESHOLD = 28
TEMP_DANGER_THRESHOLD = 35

# Maximum number of temperature values to be used as sample for the linea regression function.
TEMP_MAX_DATASET_LENGTH = 5

# Flame value threshold. [0 = fire, 1024 = No fire]
FIRE_THRESHOLD = 150


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
        config_dict = self.initial_connections(mqtt=mqtt,xml_config=xml_config)

        # Infinite loop. The program stands by for any incomming message.
        while True:
            # Call of standby_loop, to set the program waiting for a new message.
            mqtt.standby_loop()

            if (mqtt.r_message.find("SET_CN_FUNCTIONAL_MODE, active") != -1):
            # If the received message contains the phrase above, the client enters active mode.
            # Depending on the severity mode, the current state passes the mqtt connection object and the
            # dictionary as well as the severity mode to the next state.
                if(mqtt.r_message.rfind("normalMode") != -1):
                    return ActiveMode(mqtt=mqtt,config_dict=config_dict,last_known_mode="normalMode")
                elif(mqtt.r_message.rfind("warningMode") != -1):
                    return ActiveMode(mqtt=mqtt,config_dict=config_dict,last_known_mode="warningMode")
                elif(mqtt.r_message.rfind("dangerMode") != -1):
                    return ActiveMode(mqtt=mqtt, config_dict=config_dict, last_known_mode="dangerMode")
                else:
                    return ActiveMode(mqtt=mqtt, config_dict=config_dict)

            elif (mqtt.r_message.find("SET_CN_FUNCTIONAL_MODE, blocked") != -1):
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

        # Extracred data are saved in a dictionary for later use
        config_dict = {'networkName': networkName, 'serverID' : serverID,'ID':ID,
                       'country':country,'districtState':districtState,'city':city,
                       'areaDescription':areaDescription,'area':area,'building':building,
                       'room':room,'client_extra_topic':client_extra_topic}

        # The extracted data forms the final control topic.
        client_control_topic = networkName + "/" + ID + "/" + country + "/" + districtState + "/" +\
        city + "/" + areaDescription + "/" + area + "/" + building + "/" + room + "/control";
        # The topic is inserted into the dictionary
        config_dict['client_control_topic'] = client_control_topic

        print("Memory before publish:")
        print(gc.mem_free())
        # The Client publishes it's XML file to a specific topic using the "PUB_CONFIG_FILE" as a header str.
        mqtt.publish(topic=client_control_topic, msg="PUB_CONFIG_FILE, " +
        xml_config + ",parameter2, parameter3",retain=False, qos=1)

        gc.collect()
        print("Memory before subscribe:")
        print(gc.mem_free())
        # The Client subscribes to the same topic in order to get the server response.
        mqtt.subscribe(topic=client_control_topic, qos=1)

        # The function returns the extracted content list
        return config_dict


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

    # Class functionality variables.
    # Timer declaration
    timer = machine.Timer(0)
    # The dataset that will be used for the linear regression
    temp_data = []
    # An object holding the current mode of the client.
    current_mode = None

    def __init__(self,mqtt,config_dict,last_known_mode = "normalMode"):
        """ __init__ function. This is the constructor of the current state.
        Args:
            param1 (Cn2Mqtt): The mqtt object instance
            param2 (dict): A dict containing extracted data from the XML
            param3 (str): The last known mode of the program.

        """
        print('Current State: ' + str(self))

        self.mqtt = mqtt
        self.config_dict = config_dict

        # The client changes modes accordingly depending on the result from the previous state.
        next_mode = last_known_mode
        while True:
            # go_to function is responsible for mode changing.
            next_mode = self.go_to(next_mode)
            gc.collect()


    def mqtt_listener(self,mqtt,config_dict,sen_topics):
        """mqtt_client function. This function includes the main looping for incoming messages.
        Args:
            param1 (Cn2Mqtt): The mqtt object instance
            param2 (dict): A dictionary containing extracted data from the XML
            param3 (dict): A dictionary containing the sensor topics of subscription.

        """

        # Infinite loop. The program stands by for any incoming message.
        while True:
            print("listening...")
            #Call of standby_loop, to set the program waiting for a new message.
            mqtt.standby_loop()
            print(mqtt.r_topic + ": " + mqtt.r_message)
            # If the client receives a message with the specific exit message "0"
            if(mqtt.r_topic.find("node/exit") != -1 and mqtt.r_message == "0"):
                # it means that a timer interrupt occured
                # The client collects and publishes measurements.
                measurements = self.sensor_measurements(self.sensors)
                self.publish_measurements(mqtt,sen_topics,measurements)
                # Temperature is saved in a dataset for processing.
                self.temp_data.append(measurements['temp'])

                if(len(self.temp_data)>TEMP_MAX_DATASET_LENGTH):
                    # the dataset always keeps a specific length
                    # if it exceeds this length a value is removed from the list
                    self.temp_data.pop(0)
                    gc.collect()

                # If the dataset contains a specific amount of temperature measurements
                if(len(self.temp_data) > 1 and len(self.temp_data) <=TEMP_MAX_DATASET_LENGTH):
                    # The calculate calculates the temperature change rate based on the linear regression
                    #  line of the dataset
                    change_rate = self.linear_regression(self.temp_data)
                else:
                    # If the dataset contains only one value
                    change_rate = 0

                # Depending on the current mode, the client compares data values with given thresholds
                # The next mode of the node depends on these comparisons
                if (ActiveMode.current_mode == "normalMode"):
                    next_mode = self.compare_values(change_rate, measurements['temp'])
                else:
                    next_mode = self.compare_values(change_rate, measurements['temp'], measurements['flame'])

                # If there is a mode change the program exits the while loop in
                # order to change severity mode.
                if (next_mode != ActiveMode.current_mode):
                    break

            # If the client receives a message with the specific exit message "1"
            elif(mqtt.r_topic.find("node/exit") != -1 and mqtt.r_message == "1"):
                # it means that a fire pin interrupt has occured
                print("Fire ALERT !!")
                # the mode changes to warning
                next_mode = "warningMode"
                break

        gc.collect()
        # after a mode change, the timer is deinitialized.
        self.timer.deinit()
        # the function returns the next mode of the client
        return next_mode

    def active_connections(self,mqtt,config_dict):
        """active_connections function. In this function, the program acquires data from the XML
        forms and subscribes to all necessary topics.

        Args:
            param1 (Cn2Mqtt): The mqtt connection object.
            param2 (dict): A dictionary containing extracted data from the XML
        """

        # Construction of the topic.
        items = config_dict['networkName'] + "/" + config_dict['serverID'] + "/" + config_dict['country'] +\
        "/" + config_dict['districtState'] + "/" + config_dict['city'] + "/" + config_dict['areaDescription'] +\
        "/" + config_dict['area'] + "/" + config_dict['building'] + "/" + config_dict['room']

        # The client subscribes to local time and server status topic.
        sys_local_time_topic = "$SYS/" + items + "/localDateTime";
        sys_server_status_topic = "$SYS/" + items + "/" + config_dict['serverID'] + "/status";

        mqtt.subscribe(topic=sys_local_time_topic, qos=1)
        mqtt.subscribe(topic=sys_server_status_topic, qos=1)
        # Interrupt message topic
        mqtt.subscribe(topic="node/exit", qos=1)

        # If there is an extra subscription topic inside the client's XML file, the client subscribes to it.
        if(config_dict['client_extra_topic'] != ""):
            mqtt.subscribe(topic=config_dict['client_extra_topic'], qos=1)

        # The client node publishes it's severity mode on the server.
        # The server should always know the severity mode changes on each node.
        mqtt.publish(topic=config_dict['client_control_topic'],
                     msg="PUB_CN_SEVERITY_MODE, " + ActiveMode.current_mode +
                         ", parameter2, parameter3", retain=False, qos=1)

        print("Memory Left:")
        print(gc.mem_free())

    def sensor_setup(self,config_dict,samp_rate):
        """sensor_setup function. This function is used for the basic sensor and 
        variable setup of the current mode

        Args:
            param1 (dict): A dictionary containing extracted data from the XML
            param2 (int): The sensor's sampling rate
        """

        # A list that contains all the sensor topics
        s_topics = []

        # Topics are formed by the already extracted data
        sensor_topic = config_dict['networkName'] +"/"+ config_dict['ID'] +"/"+ config_dict['country'] +"/"+\
        config_dict['districtState'] +"/"+ config_dict['city'] +"/"+ config_dict['areaDescription'] +"/"+\
        config_dict['area'] +"/"+ config_dict['building'] +"/"+ config_dict['room']
        fire_topic = sensor_topic + "/indoorFlameSensor"
        temperature_topic = sensor_topic + "/indoorTemperatureSensor"
        humidity_topic = sensor_topic + "/indoorHumiditySensor"

        s_topics.append(fire_topic)
        s_topics.append(temperature_topic)
        s_topics.append(humidity_topic)

        gc.collect()

        # The timer is set depending on the sampling rate.
        self.set_timer(samp_rate)
        # The Sensors object is initialized
        if(ActiveMode.current_mode == "normalMode"):
            # If in normal mode, the fire measurements are not taken and the pin interrupt trigger is set instead.
            self.sensors = Sensors(self.fire_pin_interrupt)
        else:
            self.sensors = Sensors()

        return s_topics

    def set_timer(self,samp_rate):
        """set_timer function. This function is used to set the timer interrupt.
        Args:
            param1 (int): The sensor's sampling rate
        """

        # We set the timer as periodic (repeat it self) and a calback function to handle the interrupt.
        self.timer.init(period=samp_rate*1000, mode=machine.Timer.PERIODIC, callback=self.timer_interrupt)


    def sensor_measurements(self,sensors):
        """sensor_measurements function. This function is used collect data from the sensors
        depending on the severity mode.
        
        Args:
            param1 (Sensors): The sensors object instance.
        """

        # Measurements are saved in a dictionary
        measurements = {}
        if (ActiveMode.current_mode != "normalMode"):
            fire_value = sensors.get_fire_value()
            time.sleep(0.05)
            measurements['flame'] = fire_value
        readings = sensors.get_temp_hum_status()
        time.sleep(0.05)
        measurements['temp'] = readings[0]
        measurements['hum'] = readings[1]
        gc.collect()
        print(measurements)
        return measurements

    def publish_measurements(self,mqtt,sensor_topics,sensor_data):
        """publish_measurements function. This function is responsible for
        publishing the data to their topics.

        Args:
            param1 (Cn2Mqtt): The mqtt connection object.
            param2 (dict): A dictionary containing the sensor topics
            param3 (dict): A dictionary containing the sensor data
        """

        # If the client node is not in normal mode, flame sensor data are included in the measurements
        if (ActiveMode.current_mode != "normalMode"):
            mqtt.publish(topic=sensor_topics[0], msg="int,0-1024," + str(sensor_data['flame']), retain=False, qos=1)

        mqtt.publish(topic=sensor_topics[1], msg="float,0-70," + str(sensor_data['temp']), retain=False, qos=1)
        mqtt.publish(topic=sensor_topics[2], msg="float,0-100," + str(sensor_data['hum']), retain=False, qos=1)

        print("Published measurements")
        gc.collect()

    def get_next_mode(self):
        """get_next_mode function. Getter function for the next_mode object.
        """
        return self.next_mode

    def go_to(self,next_mode):
        """go_to function. This function is used to change the modes of the client node.

        Args:
            param1 (str): The target mode
        """

        # We import the severity mode classes
        import cn2_sev_modes as modes
        gc.collect()

        # and change the client's mode accordingly.
        if(next_mode == "normalMode"):
            print("Changing to normalMode")
            # Current_mode class variable is updated on every change
            ActiveMode.current_mode = "normalMode"
            # The new mode is initiated
            self.state = modes.NormalMode(self.mqtt, self.config_dict)
            # every mode object returns the next mode (target mode)
            next_mode = self.state.get_next_mode()
        elif(next_mode == "warningMode"):
            print("Changing to Warning")
            ActiveMode.current_mode = "warningMode"
            self.state = modes.WarningMode(self.mqtt, self.config_dict)
            next_mode = self.state.get_next_mode()
        elif (next_mode == "dangerMode"):
            print("Changing to Danger")
            ActiveMode.current_mode = "dangerMode"
            self.state = modes.DangerMode(self.mqtt, self.config_dict)
            next_mode = self.state.get_next_mode()
        return next_mode

    def linear_regression(self,data):
        """linear_regression function. This function processes the data from the last number of 
        temperature measurements and calculates the temperature change rate.

        Args:
            param1 (list): The dataset
        """

        if (ActiveMode.current_mode == "normalMode"):
            time = 60
        elif (ActiveMode.current_mode == "warningMode"):
            time = 40
        else:
            time = 20

        Sum_X = 0
        Sum_Y = 0
        Sum_XY = 0
        Sum_X2 = 0

        #data = [21.1,22.7,24.4,26.2,28.5]
        time = [40,80,120,160,200]

        # Calculations based on the dataset
        for n in range(len(data)):
            Sum_X = Sum_X + time[n]
            Sum_Y = Sum_Y + float(data[n])
            Sum_XY = Sum_XY + (time[n] * float(data[n]))
            Sum_X2 = Sum_X2 + time[n]**2


        n = len(data)

        change_rate = ((n*Sum_XY)-(Sum_X*Sum_Y))/((n*Sum_X2)-Sum_X**2)
        # convert rate/time to rate/minute
        change_rate = float(60 * change_rate)/60

        print (change_rate)
        # return the absolute value of change_rate
        return abs(change_rate)

    def compare_values(self,change_rate,temp_value,flame_value=None):
        """compare_values function. This function compares the collected data and makes 
        decisions for the next mode of the client mode
        Args:
            param1 (float): The change rate of the last temperature samples
            param2 (int): Current temeperature value
            param3 (int): Current flame value
        """

        # Decision making based on data collection. Fire value, ambient temperature value
        # and the progress of temperature have a major role on decision making.
        if flame_value is not None:
            print(flame_value)
            if(flame_value < FIRE_THRESHOLD):
                print("Danger Fire!")
                return "dangerMode"


        if(change_rate < TEMP_CHANGE_RATE_WARNING_THRESHOLD):
            if(temp_value < TEMP_WARNING_THRESHOLD):
                print("Normal temp")
                next_mode = "normalMode"
            elif(temp_value < TEMP_DANGER_THRESHOLD):
                print("Warning temp")
                next_mode = "warningMode"
            else:
                print("Danger temp")
                next_mode = "dangerMode"


        elif(change_rate < TEMP_CHANGE_RATE_DANGER_THRESHOLD):
            if(temp_value < TEMP_DANGER_THRESHOLD):
                print("Warning temp")
                next_mode = "warningMode"
            else:
                print("Danger temp")
                next_mode = "dangerMode"
        else:
            print("Danger temp")
            next_mode = "dangerMode"

        return next_mode



    def timer_interrupt(self,timer):
        """timer_interrupt function. This special function is executed after the timer
        interupt occurance. It's main purpose is to inform the program about the interrupt.
        To do that the client sends an exit mqtt message to break the wait_msg loop.

        Args:
            param1 (timer): The timer object
        """
        print("timer interrupt")
        self.mqtt.publish(topic="node/exit", msg="0", retain=False, qos=1)
        gc.collect()


    def fire_pin_interrupt(self,pin):
        """fire_pin_interrupt function. This special function is executed after the pin
        interupt occurance. The interrupt must be handled only in normal mode. If the client's mode 
        is different than normal, the interrupt is ignored.

        Args:
            param1 (Pin): The pin object
        """
        if(ActiveMode.current_mode == "normalMode"):
            print("pin interrupt")
            # To disengage the pin trigger we temporarily set the pin to PWM mode.
            # This is done to avoid false pin triggering during the interrupt handling.
            PWMpin = machine.PWM(pin)
            self.mqtt.publish(topic="node/exit", msg="1", retain=False, qos=1)
            PWMpin.deinit()














