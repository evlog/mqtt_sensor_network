"""
    File name: state.py
    Author: Georgios Vrettos
    Date created: 18/12/2017
    Date last modified: 18/12/2017
    Micropython Version: 1.9.3


Todo :
	* 

"""


# Global variables
# --------------------------------------------------------------------------------------------------


# --------------------------------------------------------------------------------------------------



class State(object):
    """
    The state class represents the state of an object, 
    in our case the state of our device (client program)

    """

    def __init__(self):
        """ __init__ function. This is the constructor of the state class.
        """

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

