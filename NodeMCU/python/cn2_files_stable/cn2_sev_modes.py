"""
    File name: cn2_sev_modes.py
    Author: Georgios Vrettos
    Date created: 21/2/2018
    Date last modified: 13/3/2018
    Micropython Version: 1.9.3


This module contains the severity modes' classes and their functions.

Todo :
	* 

"""

import gc
gc.collect()
from cn2_states import ActiveMode
import machine




# Global variables
# --------------------------------------------------------------------------------------------------

# Sampling rate varies between the client's modes.
NORMAL_SAMPLING_RATE = 60
WARNING_SAMPLING_RATE = 40
DANGER_SAMPLING_RATE = 20

# --------------------------------------------------------------------------------------------------


class NormalMode(ActiveMode):
    """
    This mode is used as the default monitoring mode. Sampling rate is set to 60 seconds
    for temperature and humidity. Fire alert is activated only on pin value change.
    """

    def __init__(self,mqtt,config_dict):
        """ __init__ function. This is the constructor of the current mode.
        Args:
            param1 (Cn2Mqtt): The mqtt object instance
            param2 (dict): A dictionary containing extracted data from the XML

        """
        print('Current Mode: ' + ActiveMode.current_mode)

        gc.collect()
        print("Memory in Normal Mode:")
        print(gc.mem_free())

        self.mqtt = mqtt

        # After entering active mode, the client subscribes to the necessary topics.
        self.active_connections(self.mqtt,config_dict)
        gc.collect()

        sampling_rate = NORMAL_SAMPLING_RATE

        # sensor_setup function is called for the inital setup of the sensors.
        sensor_topics = self.sensor_setup(config_dict, sampling_rate)

        # The function that initiates the loop of the program.
        self.next_mode = self.mqtt_listener(self.mqtt,config_dict,sensor_topics)
        # This function returns the next mode of the program (in case of mode change)


class WarningMode(ActiveMode):
    """
    
    This is the second mode in which the system enters in case of an series of events.
    """

    def __init__(self,mqtt,config_dict):
        """ __init__ function. This is the constructor of the current mode.
        Args:
            param1 (Cn2Mqtt): The mqtt object instance
            param2 (dict): A dictionary containing extracted data from the XML

        """
        print('Current Mode: ' + ActiveMode.current_mode)

        gc.collect()
        print("Memory in Warning Mode:")
        print(gc.mem_free())

        self.mqtt = mqtt

        self.active_connections(self.mqtt,config_dict)
        gc.collect()

        sampling_rate = WARNING_SAMPLING_RATE

        sensor_topics = self.sensor_setup(config_dict, sampling_rate)

        # The function that initiates the loop of the program.
        self.next_mode = self.mqtt_listener(self.mqtt,config_dict,sensor_topics)



class DangerMode(ActiveMode):
    """
    This is the third mode of the client.
    """

    # Class functionality variables.

    def __init__(self,mqtt,config_dict):
        """ __init__ function. This is the constructor of the current mode.
        Args:
            param1 (Cn2Mqtt): The mqtt object instance
            param2 (dict): A dictionary containing extracted data from the XML

        """
        print('Current Mode: ' + ActiveMode.current_mode)

        gc.collect()
        print("Memory in Danger Mode:")
        print(gc.mem_free())

        self.mqtt = mqtt

        # After entering active mode, the client subscribes to the necessary topics.
        self.active_connections(self.mqtt,config_dict)
        gc.collect()


        sampling_rate = DANGER_SAMPLING_RATE

        sensor_topics = self.sensor_setup(config_dict, sampling_rate)

        # The function that initiates the loop of the program.
        self.next_mode = self.mqtt_listener(self.mqtt,config_dict,sensor_topics)
