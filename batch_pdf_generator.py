import os
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from parse_xml import parse_xml

def draw_imposition_section(c, section, sheet_x, sheet_y):
    printing = section['printing']
    impo = printing.get('imposition', {})

    across_x = int(impo.get('across_x'))
    across_y = int(impo.get('across_y'))
    size_x = float(impo.get('size_x'))
    size_y = float(impo.get('size_y'))
    bleed = float(impo.get('bleed')) if impo.get('bleed') else 0
    grip_x1 = float(impo.get('grip_x1'))
    grip_y1 = float(impo.get('grip_y1'))
    printable_x = float(impo.get('printable_x'))
    printable_y = float(impo.get('printable_y'))

    trim_width = size_x - 2 * bleed
    trim_height = size_y - 2 * bleed

    total_width = across_x * size_x
    total_height = across_y * size_y

    offset_x = (printable_x - total_width) / 2 + (sheet_x - printable_x) / 2
    offset_y = (printable_y - total_height) / 2 + (sheet_y - printable_y) / 2

    c.setPageSize((sheet_x * inch, sheet_y * inch))

    for row in range(across_y):
        for col in range(across_x):
            x = (offset_x + col * size_x + bleed) * inch
            y = (sheet_y - (offset_y + row * size_y + bleed + trim_height)) * inch

            c.setLineWidth(1.5)
            c.setStrokeColorRGB(0, 0, 0)

            # Crop marks at trim box
            cx, cy = x, y + trim_height * inch
            c.line(cx - 0.0625 * inch, cy, cx, cy)
            c.line(cx, cy + 0.125 * inch, cx, cy)
            cx2 = x + trim_width * inch
            c.line(cx2, cy, cx2 + 0.0625 * inch, cy)
            c.line(cx2, cy + 0.125 * inch, cx2, cy)
            bx, by = x, y
            c.line(bx - 0.0625 * inch, by, bx, by)
            c.line(bx, by - 0.125 * inch, bx, by)
            brx, bry = bx + trim_width * inch, by
            c.line(brx, bry, brx + 0.0625 * inch, bry)
            c.line(brx, bry - 0.125 * inch, brx, bry)

    c.showPage()
    c.save()

def process_all_xml():
    input_folder = 'XML Files'
    output_folder = 'Output PDFs'
    os.makedirs(output_folder, exist_ok=True)

    for file in os.listdir(input_folder):
        if file.endswith('.xml'):
            path = os.path.join(input_folder, file)
            sections = parse_xml(path)
            if not sections:
                print(f"No sections found in {file}")
                continue

            output_pdf = os.path.join(output_folder, f"{os.path.splitext(file)[0]}_imposed.pdf")
            sheet_x = float(sections[0]['printing']['imposition']['sheet_x'])
            sheet_y = float(sections[0]['printing']['imposition']['sheet_y'])

            c = canvas.Canvas(output_pdf)
            draw_imposition_section(c, sections[0], sheet_x, sheet_y)
            print(f"✅ Generated: {output_pdf}")

if __name__ == "__main__":
    process_all_xml()
