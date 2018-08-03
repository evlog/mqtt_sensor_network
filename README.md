In this project we created a small scale network application combining different hw devices on the same software core. Our alert-based sensor system utilizes the MQTT protocol with TLS encryption to share data between three network nodes a) A Raspberry Pi (CN1) b) an ESP8266 (CN2)  c) a PC Server (SN). We focus on the formalization of the protocol’s basic elements by strictly defining the topic/message scheme. On this repository we include the software used for the nodes as well as other necessary files for each platform. 

Repository content
--------

*  [Raspberry Pi (CN1) files](https://github.com/evlog/mqtt_sensor_network/tree/master/RaspberryPi)
*  [ESP8266 (CN2) files](https://github.com/evlog/mqtt_sensor_network/tree/master/NodeMCU)
*  [Server (SN) files](https://github.com/evlog/mqtt_sensor_network/tree/master/server)
*  [Code related documents](https://github.com/evlog/mqtt_sensor_network/tree/master/docs)
*  [Test files](https://github.com/evlog/mqtt_sensor_network/tree/master/tests)

Network topology
--------
The topology of our network architecture is presented in the following figure. Locally, the highest level of the network is a Linux server running the MQTT broker (level #2), and managing the database, which collects incoming data, and an efficient dashboard to present these data, in a meaningful way, to system administrators. The server might also have high performance computing capabilities to process data and may also push data to other cloud platforms (level #3), like ThingSpeak, Google Cloud, etc. The server may collect data directly from low level MQTT client nodes at the edge of the network (level #0), or intermediate levels with more powerful nodes (level #1) may filter/compress data to reduce network traffic. Nodes at level #0 do not establish long-lived connections with the broker but rather communicate in an alert-based manner to report data periodically or based on interrup/timeout events. Although these nodes make use of very low-end hardware, we want themto be able to: a) connect to the MQTT broker over local/long range WiFi or 3G/4G networks, b) get into low-power/sleep mode to save power, but also include hardware that can support MQTT message encryption using the Transport Layer Security (TLS) protocol, c) support software execution using threading and/or interrupts to handle MQTT traffic, as well as interrupt events from connected sensors, d) support, if possible, Operating System (OS) and file based software, and e) support Over the Air (OtA) re-programming and configuration.

<img src="https://github.com/evlog/mqtt_sensor_network/blob/master/html/figures/network_topology_low.jpg" width="800" class="center/>

Code
--------

As a programing platform we used Python 2.7 for the Raspberry Pi and the Server node. For the ESP8266 a lite version of Python 3 for uCs was used, Micropython.


XML node configuration file content
--------

We define the settings for every node using XML configuration files based on this [XML schema](https://github.com/evlog/mqtt_sensor_network/blob/master/server/xml/node_config_schema.xsd). An XML schema tree diagram is available [here](https://github.com/evlog/mqtt_sensor_network/blob/master/server/xml/node_config_schema.svg). The most important XML elements are listed below:

*  Geolocation information
*  Type of hardware and attached sensors
*  Type of software and OS
*  Type of data types proviced by the sensors
*  network parameters (ID, IP, etc.)

The content of the configuration file is parsed during hardware boot by every node and also transmitted by each CN to the SN during a connection/validation process, where the SN validates the XML file against the definded XML schema. In case of an invalid XML file from a node, the SN blocks that node.


Server node (SN)
--------

<img src="https://github.com/evlog/mqtt_sensor_network/blob/master/readme_files/sn_state_diagram.png" />

The state diagram of the Server node is presented above. The node works like a state machine with two main states a) active and b) blocked. On active state after it’s own XML configuration file validation the SN stands by for incoming MQTT messages. In the event of a new client connection attempt the client’s XML is being checked and if it is valid SN sets the functional and severity mode of the CN based on it’s last known state.  If a data message is received. containing sensor measurements, data is processed and saved into the database. The SN is always aware of a sudden severity mode change on it’s client nodes.

Client nodes (CNs)
--------

<img src="https://github.com/evlog/mqtt_sensor_network/blob/master/readme_files/cn2_state_diagram.png" />

Client nodes also work as state machines. After their connection/validation attempt using their XML configuration file, nodes begin the sensor sampling process and measurement publishments in timed intervals. On a pin interrupt (Alert) a client node values the severity of the situation and changes mode on demand. CNs are always listening to incoming MQTT commands.


The Project
--------
 
This project is part of a research program that takes place at the University of the Aegean (Department of Information 
& Communication Systems Engineering), based in the island of Samos (city of Karlovasi) in Greece, focusing on a small scale Internet of Things network. Main contributors are listed below:

Evangelos Logaras  -  evangelos.logaras@infineon.com  
Georgios Vrettos  -  gvrettos@aegean.gr  
Emmanouil Kalligeros  -  kalliger@aegean.gr

Publications
--------
G. Vrettos, E. Logaras, and E. Kalligeros, "Towards standardization of MQTT-alert-based sensor networks: protocol structures formalization and low-end node security", in *Proc. of IEEE International Symposium on Industrial Embedded Systems (SIES)*, June 2018.






