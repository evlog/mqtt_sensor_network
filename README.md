In this project we created a small scale network application combining different hw devices on the same software core. Our alert-based sensor system utilizes the MQTT protocol with TLS encryption to share data between three network nodes a) An ESP8266 b) a Raspberry Pi c) a PC Server. We focus on the formalization of the protocol’s basic elements by strictly defining the topic/message scheme. On this repository we include the software used for the nodes as well as other necessary files for each platform. We also define the settings for every node using XML configuration files based on a [XML schema](https://github.com/evlog/mqtt_sensor_network/blob/master/server/xml/node_config_schema.xsd).  

Repository content
--------

*  [ESP8266 (NodeMCU) files](https://github.com/evlog/mqtt_sensor_network/tree/master/NodeMCU)
*  [Raspberry Pi files](https://github.com/evlog/mqtt_sensor_network/tree/master/RaspberryPi)
*  [Server files](https://github.com/evlog/mqtt_sensor_network/tree/master/server)
*  [Code related documents](https://github.com/evlog/mqtt_sensor_network/tree/master/docs)
*  [Test files](https://github.com/evlog/mqtt_sensor_network/tree/master/tests)

Code
--------

As a programing platform we used Python 2.7 for the Raspberry Pi and the Server node. For the ESP8266 a lite version of Python 3 for uCs was used, Micropython.


XML node configuration file content
--------

*  Geolocation information
*  Type of hardware and attached sensors
*  Type of software and OS
*  Type of data types proviced by the sensors
*  network parameters (ID, IP, etc.)


Server node
--------

<img src="https://github.com/evlog/mqtt_sensor_network/blob/master/readme_files/sn_state_diagram.png"/>

Client nodes
--------

<img src="https://github.com/evlog/mqtt_sensor_network/blob/master/readme_files/cn2_state_diagram.png"/>








