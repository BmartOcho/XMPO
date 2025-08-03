import xml.etree.ElementTree as ET
import re

def get_ns(tag):
    m = re.match(r'\{.*\}', tag)
    return m.group(0) if m else ''

def _get_text(elem):
    return elem.text.strip() if elem is not None and elem.text else None

def parse_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    ns = get_ns(root.tag)

    all_sections = []
    sections = root.findall(f'.//{ns}Section')

    for section in sections:
        data = {
            'finished_width': _get_text(section.find(f'{ns}FinishedWidth')),
            'finished_height': _get_text(section.find(f'{ns}FinishedHeight')),
            'impo_width': _get_text(section.find(f'{ns}ImpositionWidth')),
            'impo_height': _get_text(section.find(f'{ns}ImpositionHeight')),
            'pages': _get_text(section.find(f'{ns}Pages')),
            'printing': {}
        }

        printing = section.find(f'{ns}Printing')
        if printing is not None:
            data['printing'] = {
                'sheet_width': _get_text(printing.find(f'{ns}SheetWidth')),
                'sheet_depth': _get_text(printing.find(f'{ns}SheetDepth')),
                'machine': _get_text(printing.find(f'{ns}Machine')),
                'process_front': _get_text(printing.find(f'{ns}ProcessFront')),
                'process_reverse': _get_text(printing.find(f'{ns}ProcessReverse')),
                'stock_thickness': _get_text(printing.find(f'{ns}StockThicknessValue')),
                'imposition': {}
            }

            impo = printing.find(f'{ns}Imposition')
            if impo is not None:
                data['printing']['imposition'] = {
                    'across_x': _get_text(impo.find(f'{ns}AcrossX')),
                    'across_y': _get_text(impo.find(f'{ns}AcrossY')),
                    'sheet_x': _get_text(impo.find(f'{ns}SheetX')),
                    'sheet_y': _get_text(impo.find(f'{ns}SheetY')),
                    'printable_x': _get_text(impo.find(f'{ns}PrintableX')),
                    'printable_y': _get_text(impo.find(f'{ns}PrintableY')),
                    'size_x': _get_text(impo.find(f'{ns}SizeX')),
                    'size_y': _get_text(impo.find(f'{ns}SizeY')),
                    'bleed': _get_text(impo.find(f'{ns}Bleed')),
                    'grip_x1': _get_text(impo.find(f'{ns}GripX1')),
                    'grip_x2': _get_text(impo.find(f'{ns}GripX2')),
                    'grip_y1': _get_text(impo.find(f'{ns}GripY1')),
                    'grip_y2': _get_text(impo.find(f'{ns}GripY2')),
                    'work_turn': _get_text(impo.find(f'{ns}IsWorkAndTurn')),
                    'work_tumble': _get_text(impo.find(f'{ns}IsWorkAndTumble')),
                }

        all_sections.append(data)

    return all_sections
