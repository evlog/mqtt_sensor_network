"""
    File name: sensors.py
    Author: Georgios Vrettos
    Date created: 11/2/2018
    Date last modified: 11/2/2018
    Micropython Version: 1.9.3


This module contains all the functions needed for the sensor measurements.

Todo :
	* 

"""

import machine
import dht
import time


# Global variables
# --------------------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------------------------

class Sensors():

    def __init__(self):
        """ __init__ function. This is the constructor of the measurements object.
        """

    def get_fire_status(self):

        #Analog Input (A0)
        #flame_pin = machine.ADC(0)
        #print("Flame Value: ")
        #print(flame_pin.read())

        #Digital Input (D2)
        flame_pin = machine.Pin(4)
        print("Flame Value: ")
        print(flame_pin.value())

    def get_temp_hum_status(self):

        dht11 = dht.DHT11(machine.Pin(5))
        dht11.measure()
        time.sleep(0.1)
        print("Temperature: ")
        print(dht11.temperature())
        print("°C")
        print("Humidity: ")
        print(dht11.humidity())
        print("%")


