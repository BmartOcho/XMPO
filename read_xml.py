import xml.etree.ElementTree as ET
import re

# Load and parse the XML
tree = ET.parse('XML Files/J208819.xml')
root = tree.getroot()

# Extract XML namespace
def get_ns(tag):
    m = re.match(r'\{.*\}', tag)
    return m.group(0) if m else ''

ns = get_ns(root.tag)

# Find all <Section> elements
sections = root.findall(f'.//{ns}Section')
print(f"Found {len(sections)} sections\n")

for section in sections:
    # Extract from the section itself
    fw = section.find(f'{ns}FinishedWidth')
    fh = section.find(f'{ns}FinishedHeight')
    iw = section.find(f'{ns}ImpositionWidth')
    ih = section.find(f'{ns}ImpositionHeight')
    pages = section.find(f'{ns}Pages')

    print("====Finished Size Details====")
    print("Finished Width:", fw.text if fw is not None else "None")
    print("Finished Height:", fh.text if fh is not None else "None")
    print("Imposition Width:", iw.text if iw is not None else "None")
    print("Imposition Height:", ih.text if ih is not None else "None")
    print("Pages:", pages.text if pages is not None else "None")

    # Get <Printing> block
    printing = section.find(f'{ns}Printing')
    if printing is not None:
        sw = printing.find(f'{ns}SheetWidth')
        sd = printing.find(f'{ns}SheetDepth')
        na = printing.find(f'{ns}NoAcross')
        nar = printing.find(f'{ns}NoAround')
        machine = printing.find(f'{ns}Machine')
        pf = printing.find(f'{ns}ProcessFront')
        pr = printing.find(f'{ns}ProcessReverse')
        stv = printing.find(f'{ns}StockThicknessValue')

        print("====Sheet Details====")
        print("Sheet Width:", sw.text if sw is not None else "None")
        print("Sheet Depth:", sd.text if sd is not None else "None")
        print("Across:", na.text if na is not None else "None", "Around:", nar.text if nar is not None else "None")
        print("Machine:", machine.text if machine is not None else "None")
        print("Process Front:", pf.text if pf is not None else "None")
        print("Process Reverse:", pr.text if pr is not None else "None")
        print("Stock Thickness:", stv.text if stv is not None else "None")

        # Get <Imposition> block inside <Printing>
        impo = printing.find(f'{ns}Imposition')
        if impo is not None:
            acrossx = impo.find(f'{ns}AcrossX')
            acrossy = impo.find(f'{ns}AcrossY')
            sheetx = impo.find(f'{ns}SheetX')
            sheety = impo.find(f'{ns}SheetY')
            px = impo.find(f'{ns}PrintableX')
            py = impo.find(f'{ns}PrintableY')
            sx = impo.find(f'{ns}SizeX')
            sy = impo.find(f'{ns}SizeY')
            bleed = impo.find(f'{ns}Bleed')
            gx1 = impo.find(f'{ns}GripX1')
            gx2 = impo.find(f'{ns}GripX2')
            gy1 = impo.find(f'{ns}GripY1')
            gy2 = impo.find(f'{ns}GripY2')
            wturn = impo.find(f'{ns}IsWorkAndTurn')
            wtumble = impo.find(f'{ns}IsWorkAndTumble')

            print("====Imposition Details====")
            print("AcrossX:", acrossx.text if acrossx is not None else "None")
            print("AcrossY:", acrossy.text if acrossy is not None else "None")
            print("SheetX:", sheetx.text if sheetx is not None else "None")
            print("SheetY:", sheety.text if sheety is not None else "None")
            print("PrintableX/Y:", px.text if px is not None else "None", "/", py.text if py is not None else "None")
            print("SizeX/Y:", sx.text if sx is not None else "None", "/", sy.text if sy is not None else "None")
            print("Bleed:", bleed.text if bleed is not None else "None")
            print("GripX1/X2:", gx1.text if gx1 is not None else "None", "/", gx2.text if gx2 is not None else "None")
            print("GripY1/Y2:", gy1.text if gy1 is not None else "None", "/", gy2.text if gy2 is not None else "None")
            print("Work‑and‑Turn:", wturn.text if wturn is not None else "None")
            print("Work‑and‑Tumble:", wtumble.text if wtumble is not None else "None")

    print("-------------------\n")
