"""
    File name: state.py
    Author: Georgios Vrettos
    Date created: 11/12/2017
    Date last modified: 14/12/2017
    Python Version: 2.7


Todo :
	* 

"""

# Global variables
# --------------------------------------------------------------------------------------------------


# --------------------------------------------------------------------------------------------------



class State(object):
    """
    The state class represents the state of an object, 
    in our case the state of our device (server program)
    
    """

    def __init__(self):
        """ __init__ function. This is the constructor of the state class.
        """


    def on_event(self,event):
        """
        Handle state events
        """
        pass

    def __repr__(self):
        """
        Leverages the __str__ method to describe the State.
        """
        return self.__str__()

    def __str__(self):
        """
        Returns the name of the State.
        """
        return self.__class__.__name__


