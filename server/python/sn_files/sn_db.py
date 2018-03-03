"""
    File name: sn_db.py
    Author: Georgios Vrettos
    Date created: 11/12/2017
    Date last modified: 3/3/2018
    Python Version: 2.7

In this module, functions from the package "psycopg2" are used. 
To install the package using pip issue the following command:
$pip install psycopg2  

"""

import psycopg2


# Global variables
# --------------------------------------------------------------------------------------------------
DB_NAME = "IoT_thesis"
DB_USERNAME = "thesis"
DB_PASSWORD = "m3Fg9aqZX@8brmg8"
DB_HOST = "195.251.166.202"
DB_PORT = "5432"

# --------------------------------------------------------------------------------------------------


class Sn_db:
    ''' Base class for the DB connection handler. It contains all 
        the necessary functions concerning the database functionalities.
    '''

    # Class functionality variables.

    # This variable holds the connection object and is widely used across many functions.
    conn = ""

    def connect_db(self):
        """connect_db function. This function is used for the database connection.
        Args:
            param1 (Sn_db): Object instance
        """

        #Connecting to database using the connect function from the "psycopg2" package.
        # As parameters we use the database name, username and password as well as host address and port.
        try:
            self.conn = psycopg2.connect(database=DB_NAME, user=DB_USERNAME,
                                         password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)

        except psycopg2.DatabaseError, exception:
            print exception



    def upsert_node_db(self,data,datetime):
        """upsert_db function. This function is used 
        to insert or update node configuration data inside the database.
        Args:
            param1 (conn): The connection instance
            param2 (str): The data to be inserted into the dataabase
            param3 (str): The current timestamp
        """

        # Node id extraction from the configuration file.
        id_start = data.find('"ID": "')
        id_end = data.find('"',id_start + len('"ID": "'))
        node_id = data[id_start + len('"ID": "'):id_end]

        #A cursor for handling the queries is created
        cur = self.conn.cursor()
        #The final insertion query
        query = "INSERT INTO nodes (node_id, node_config, last_connected) VALUES " + \
                "('" + node_id + "','" + data + "','" + datetime + "') " + \
                "ON CONFLICT (node_id) DO UPDATE SET node_config = '" +\
                data + "', last_connected = '" + datetime + "';"

        #Query execution and database commit.
        cur.execute(query)
        self.conn.commit()
        print "Record inserted successfully"
        # After data insertion, the server saves all node configurations on a JSON file.
        self.backup_node_config();


    def get_node_status(self,node_id):
        """get_node_status function. This function is used 
        to get the status of a selected node.
        Args:
            param1 (conn): The connection instance
            param2 (str): The selected node.

        """

        #A cursor for handling the queries is created
        cur = self.conn.cursor()

        # The selection query
        query = "SELECT node_status FROM nodes WHERE node_id = '" + node_id + "';"
        # Query execution.
        cur.execute(query)

        row = cur.fetchone()
        # The function returns the status of the selected node.
        return row[0]


    def get_active_nodes_count(self):
        """get_active_nodes_count function. This function is used 
        to get the number of the active nodes.
        Args:
            param1 (conn): The connection instance
        """
        #A cursor for handling the queries is created
        cur = self.conn.cursor()

        # The selection query
        query = "SELECT COUNT (*) FROM nodes WHERE node_status = 'active';"

        # Query execution.
        cur.execute(query)

        row = cur.fetchone()
        # the result is parsed to integer before return.
        return int(row[0])

    def get_node_sev_mode(self,node_id):
        """get_node_sev_mode function. This function is used 
        to get the severity mode of a specific node.
        Args:
            param1 (conn): The connection instance
            param2 (str): The ID of the node

        """

        #A cursor for handling the queries is created
        cur = self.conn.cursor()

        # The selection query
        query = "SELECT sev_mode FROM nodes WHERE node_id = '" + node_id + "';"
        # Query execution.
        cur.execute(query)

        row = cur.fetchone()
        # The function returns the severity mode of the selected node.
        return row[0]

    def update_node_column(self,column, data, node_id):
        """update_node_column function. This function is used 
        to update a single column of the selected node.
        Args:
            param1 (conn): The connection instance
            param2 (str): The data to be updated on the database
            param3 (str): The ID of the node
        """

        #A cursor for handling the queries is created
        cur = self.conn.cursor()
        #The final update query
        query = "UPDATE nodes SET " + column + "='" + data + \
                "' WHERE node_id = '" + node_id + "';"

        #Query execution and database commit.
        cur.execute(query)
        self.conn.commit()
        print "Node updated successfully"



    def backup_node_config(self):
        """backup_table function. This function is used 
        to retrieve JSON data from the database and save tha data to a file
        Args:
            param1 (conn): The connection instance
        """
        # A cursor for handling the queries is created
        cur = self.conn.cursor()

        # The selection query
        query = "SELECT cast(node_config as text) FROM nodes;"

        # Query execution.
        cur.execute(query)
        rows = cur.fetchall()

        # File operations. Fetched data must be stored with the correct format.
        file = open("nodes_config.json","w")
        file_str = '{"nodes":['

        for row in rows:
            # Every new table line fetched from the server, is added to the string.
            file_str = file_str + (row[0]) + ",\n"

        # Some final string formating.
        file_str = file_str[:-2] + "]}"
        # The string content is being written on the JSON file.
        file.write(file_str)
        file.close()
        print("Configuration file saved.")


    def disconnect_db(self):
        """disconnect_db function. This function is used for database disconnect.
        Args:
            param1 (DbHandler): Object instance
        """

        self.conn.close()
