"""
    File name: cn2_machine.py
    Author: Georgios Vrettos
    Date created: 6/1/2018
    Date last modified: 6/1/2018
    Micropython Version: 1.9.3


Todo :
	* 

"""

from cn2_states import InitialMode

# Global variables
# --------------------------------------------------------------------------------------------------


# --------------------------------------------------------------------------------------------------



class Client2Machine(object):
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

