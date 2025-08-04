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

            mark_offset = 0.0625 * inch
            mark_length = 0.25 * inch

            # Top left
            cx, cy = x, y + trim_height * inch
            c.line(cx - mark_offset, cy, cx - mark_offset + mark_length, cy)
            c.line(cx, cy + mark_offset, cx, cy + mark_offset - mark_length)

            # Top right
            cx2 = x + trim_width * inch
            c.line(cx2 + mark_offset, cy, cx2 + mark_offset - mark_length, cy)
            c.line(cx2, cy + mark_offset, cx2, cy + mark_offset - mark_length)

            # Bottom left
            bx, by = x, y
            c.line(bx - mark_offset, by, bx - mark_offset + mark_length, by)
            c.line(bx, by - mark_offset, bx, by - mark_offset + mark_length)

            # Bottom right
            brx, bry = bx + trim_width * inch, by
            c.line(brx + mark_offset, bry, brx + mark_offset - mark_length, bry)
            c.line(brx, bry - mark_offset, brx, bry - mark_offset + mark_length)

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
