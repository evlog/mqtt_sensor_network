"""
    File name: validate_xml.py
    Author: Evangelos Logaras
    Date created: 24/10/2017
    Date last modified: 11/12/2017 (By Georgios Vrettos)
    Python Version: 2.7

Using functions of the lxml package to validate the structure of the XML node configuration files
against the provided XML schema.  The lxml package can be installed under Windows or Linux using  
pip:
$pip install lxml

Example:
    $ python validate_xml.py
#-------------------------------------------------------------------------------------------------- 
"""

from lxml import etree, objectify
from lxml.etree import XMLSyntaxError

# Global variables
#--------------------------------------------------------------------------------------------------

XSD_FILE_PATH = "/home/vrettel/Dropbox/Thesis/Code/PC Server/sn_files/node_config_schema.xsd"
#--------------------------------------------------------------------------------------------------

class XmlValidator:

    def xml_validator(self,xml_string):
        """XML validation function against provided XSD schema.
    
        Args:
            param1 (str): XML file content.
        """

        try:
            schema = etree.XMLSchema(file=XSD_FILE_PATH)
            parser = objectify.makeparser(schema=schema)
            objectify.fromstring(xml_string, parser)
            print("XML file has been validated.")
            return True
        except XMLSyntaxError:
            #handle exception here
            print("XML file cannot be validated.")
            return False




