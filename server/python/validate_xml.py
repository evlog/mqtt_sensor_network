"""
    File name: validate_xml.py
    Author: Evangelos Logaras
    Date created: 24/10/2017
    Date last modified: 25/10/2017
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
XML_FILE_PATH = "J:\\backup\Anakin_backup_20110812\ergasies\kapodistrian\AegeanUniversity\\" \
                "IoT_project\XML\\node_config.xml"

XSD_FILE_PATH = "J:\\backup\Anakin_backup_20110812\ergasies\kapodistrian\AegeanUniversity\\" \
                "IoT_project\XML\\node_config_schema.xsd"
#--------------------------------------------------------------------------------------------------

def xml_validator(xml_string, xsd_file_path):
    """XML validation function against provided XSD schema.

    Args:
        param1 (str): XML file content.
        param2 (str): XSD schema file path.
    """
    
    try:
        schema = etree.XMLSchema(file=xsd_file_path)
        parser = objectify.makeparser(schema=schema)
        objectify.fromstring(xml_string, parser)
        print("XML file has been validated.")
    except XMLSyntaxError:
        #handle exception here
        print("XML file cannot be validated.")
        pass

def main():
    # Read XML file
    xml_file = open(XML_FILE_PATH, 'r')
    xml_string = xml_file.read()
    xml_file.close()

    # Call the XML validation function
    xml_validator(xml_string, XSD_FILE_PATH)
    
if __name__ == "__main__":
    main()