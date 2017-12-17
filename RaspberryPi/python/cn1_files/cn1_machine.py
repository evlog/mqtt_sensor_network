"""
    File name: cn1_machine.py
    Author: Georgios Vrettos
    Date created: 10/12/2017
    Date last modified: 14/12/2017
    Python Version: 2.7


Todo :
	* 

"""

from cn1_states import InitialMode

# Global variables
# --------------------------------------------------------------------------------------------------


# --------------------------------------------------------------------------------------------------



class Client1Machine(object):
    """ 
    This class describes our main client device as a state machine.
    """

    def __init__(self):
        """ __init__ function. This is the constructor of the state machine class.
            The client machine starts with the Initial mode enabled my default.
        """

        # The machine enters Initial mode on startup.
        # This is done by setting the state object as an Initial one.
        self.state = InitialMode()

    def on_event(self,event):
        """
        This function is responsible of changing the state of the machine
        according to the event type. This method is used only when
        we want to change the state manually.
        Args:
            param1 (str): This parameter defines the target state.
        """

        # This is used to toggle the machine state depending on the current state and the event type.
        self.state = self.state.on_event(event)