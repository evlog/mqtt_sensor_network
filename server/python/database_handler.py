"""
    File name: database_handler.py
    Author: Georgios Vrettos
    Date created: 02/11/2017
    Date last modified: 06/11/2017
    Python Version: 2.7

In this module, functions from the package "psycopg2" are used. 
To install the package using pip issue the following command:
$pip install psycopg2  

"""

import psycopg2


# Global variables
# --------------------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------------------------


class DbHandler:

    def connect_db(self,record):
        """connect_db function. This function is used for the database connection.
        Args:
            param1 (DbHandler): Object instance
            param2 (str): The record to be inserted into the database.
        """

        #Connecting to database using the connect function from the "psycopg2" package.
        # As parameters we use the database name, username and password as well as host address and port.
        try:
            conn = psycopg2.connect(database="IoT_thesis", user="thesis", password="m3Fg9aqZX@8brmg8", host="localhost", port="5432")

            #After a successfull connection, we call the insert funtion.
            self.insert_db(conn,record)
        except psycopg2.DatabaseError, exception:
            print exception
        finally:
            conn.close()


    def insert_db(self,conn,data):
        """insert_db function. This function is used 
        to insert the string into the json file inside the database.
        Args:
            param1 (conn): The connection instance
            param2 (str): The data to be inserted into the dataabase
        """

        #A cursor for handling the queries is created
        cur = conn.cursor()
        #The final insertion query
        query = "INSERT INTO readings (data) VALUES ('" + data + "');"
        #Query execution and database commit.
        cur.execute(query)
        conn.commit()
        print "Record inserted successfully"