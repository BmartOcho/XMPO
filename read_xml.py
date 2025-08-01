import xml.etree.ElementTree as ET

# Load the XML file
tree = ET.parse('XML Files/J208819.xml')
root = tree.getroot()

for elem in root.iter():
    text = elem.text.strip() if elem.text and elem.text.strip() else "None"
    print(f"Tag: {elem.tag}, Text: {text}")

sections = root.findall('.//Section')

for section in sections:
    finished_width = section.find('FinishedWidth')
    finished_height = section.find('FinishedHeight')
    pages = section.find('Pages')
    sheet_width = section.find('SheetWidth')
    sheet_height = section.find('SheetHeight')
    