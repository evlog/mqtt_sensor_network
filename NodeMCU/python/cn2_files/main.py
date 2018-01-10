"""
    File name: main.py
    Author: Georgios Vrettos
    Date created: 6/1/2018
    Date last modified: 10/1/2018
    Micropython Version: 1.9.3


Todo :
	* 

"""
import gc
gc.collect()
from cn2_machine import Client2Machine



# Global variables
# --------------------------------------------------------------------------------------------------


# --------------------------------------------------------------------------------------------------


class cn2_main(object):

    def __init__(self):
        """ __init__ function. This is the constructor of the program.
        """
        gc.collect()
        print("Initial memory:")
        print(gc.mem_free())

        if(self.wifi_connect() == True):
            # The instance of the state machine.
            machine = Client2Machine()


    def wifi_connect(self):
        """ wifi_connect function. This is used to connect the ESP2866 to the wifi network.
        """
        # Network package
        import network
        # instance of  STA_IF object, used for ESP connection interface. (Station mode)
        sta_if = network.WLAN(network.STA_IF)
        if not sta_if.isconnected():
            print('connecting to  WiFi network...')
            # activate station interface
            sta_if.active(True)
            sta_if.connect('ssid', 'password')
            while not sta_if.isconnected():
                pass
        print('network config:', sta_if.ifconfig())
        return True


program = cn2_main()


