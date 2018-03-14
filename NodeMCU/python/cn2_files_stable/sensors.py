"""
    File name: sensors.py
    Author: Georgios Vrettos
    Date created: 11/2/2018
    Date last modified: 13/3/2018
    Micropython Version: 1.9.3


This module contains all the functions needed for the sensor measurements.

Todo :
	* 

"""

import gc
import machine
import dht
import time
gc.collect()


# Global variables
# --------------------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------------------------

class Sensors():
    """
    This class represents the sensor object. A sensor object includes three kind of sensors.
    """


    def __init__(self,pin_interrupt_handler=None):
        """ __init__ function. This is the first function that is executed after the object construction.
        The input function is used for the a pin interrupt interval.
    
        Args:
            param1 (function): A callback function that is used as an interrupt handler.
        """

        # If there is a funcition as an input, it means that we are in Normal Mode.
        if pin_interrupt_handler is not None:
            # A flame input pin object is initialized on 4th GPIO pin using the esp's internal pull up resistor.
            self.flame_pin_digital = machine.Pin(4, machine.Pin.IN, machine.Pin.PULL_UP)
            # A trigger is set on this digital pin operating on the falling edge of the clock.
            # As a callback function we use a specific function imported from another module as a parameter.
            self.flame_pin_digital.irq(trigger=machine.Pin.IRQ_FALLING, handler=pin_interrupt_handler)
        else:
            # If there is no function as an input, it means that we are in Warning or Danger mode.
            # We initialize the pin as an analog pin using esp's the ADC on pin A0.
            self.flame_pin_analog = machine.ADC(0)

        # We initialize the dht temperature and humidity sensor on GPIO5
        self.dht11 = dht.DHT11(machine.Pin(5))


    def get_fire_value(self):
        """ get_fire_value function. This function returns an analog read from the flame sensor.

        """

        #Analog Input (A0)
        return self.flame_pin_analog.read()

    def get_temp_hum_status(self):
        """ get_temp_hum_status function. This function measures temperature and humidity from the digital
        pin and appends the 2 values to a list which then returns.

        """

        readings = []
        self.dht11.measure()
        time.sleep(0.15)
        readings.append(self.dht11.temperature())
        time.sleep(0.01)
        readings.append(self.dht11.humidity())
        gc.collect()
        return readings



