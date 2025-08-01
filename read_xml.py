import xml.etree.ElementTree as ET

# Load the XML file
tree = ET.parse('XML Files/J208819.xml')
root = tree.getroot()

# Print root tag
print(f"Root tag: {root.tag}")

# Traverse and print all tags and attributes
for elem in root.iter():
    print(f"Tag: {elem.tag}, Attributes: {elem.attrib}")
