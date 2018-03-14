"""
    File name: sn_thread.py
    Author: Georgios Vrettos
    Date created: 11/12/2017
    Date last modified: 12/3/2018
    Python Version: 2.7

In this module, functions from the package "threading" are used. The purpose of this module
is the construction of the thread objects that are used in our main program.


Todo :
	*
"""

import threading


# Global variables
# --------------------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------------------------


class Sn_thread (threading.Thread):
    'The thread class that contains the necessary thread attributes and functions'


    def __init__(self,id=None,data=None,callback=None):
        """__init__ function. This function is used to create the instance of the thread with 
        already set attributes.
        Args:
            param1 (str): The id of the current thread.
            param2 (obj): The data object, the type of data depends on the callback function.
            param3 (function): The callback function that is to be executed when the thread starts.
        """

        # Initalizing the thread
        threading.Thread.__init__(self)
        # We set every attribute to our thread instance.
        self.threadID = id
        self.data = data
        self.callback = callback


    def run(self):
        """run function. This function is the first function 
        that fires when after the instance creation.
        """

        print "Starting " + self.threadID
        # The appropriate callback function is called with the data obj as an input.
        self.callback(self.threadID,self.data)
        print "Exiting " + self.threadID

