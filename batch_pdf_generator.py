import os
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from parse_xml import parse_xml


def draw_imposition_section(c, section, sheet_x, sheet_y):
    """
    Draw a single section imposition onto the canvas `c`.
    Marks trimmed cards with crop marks extending outwards from each corner.
    """
    printing = section['printing']
    impo = printing.get('imposition', {})

    across = int(impo.get('across_x', 0))
    down = int(impo.get('across_y', 0))
    size_x = float(impo.get('size_x', 0))
    size_y = float(impo.get('size_y', 0))
    printable_x = float(impo.get('printable_x', sheet_x))
    printable_y = float(impo.get('printable_y', sheet_y))
    finished_w = float(impo.get('finished_width', 0))
    finished_h = float(impo.get('finished_height', 0))
    bleed = float(impo.get('bleed', 0))

    total_w = across * size_x
    total_h = down * size_y
    offset_x = (printable_x - total_w) / 2.0 + (sheet_x - printable_x) / 2.0
    offset_y = (printable_y - total_h) / 2.0 + (sheet_y - printable_y) / 2.0

    c.setPageSize((sheet_x * inch, sheet_y * inch))
    c.setLineWidth(1.5)  # 1.5 points thickness
    c.setStrokeColorRGB(0, 0, 0)

    mark_offset = 0.0625 * inch  # 1/16" outside trim edge
    mark_length = 0.125 * inch   # 1/8" long crop mark

    for row in range(down):
        for col in range(across):
            trim_x = (offset_x + col * size_x) * inch
            trim_y = (offset_y + row * size_y) * inch

            left = trim_x
            bottom = trim_y
            right = left + finished_w * inch
            top = bottom + finished_h * inch

            # Crop marks at each corner extending out from trim edges
            # Top-left
            c.line(left - mark_offset, top, left - mark_offset + mark_length, top)
            c.line(left, top + mark_offset, left, top + mark_offset - mark_length)

            # Top-right
            c.line(right + mark_offset, top, right + mark_offset - mark_length, top)
            c.line(right, top + mark_offset, right, top + mark_offset - mark_length)

            # Bottom-left
            c.line(left - mark_offset, bottom, left - mark_offset + mark_length, bottom)
            c.line(left, bottom - mark_offset, left, bottom - mark_offset + mark_length)

            # Bottom-right
            c.line(right + mark_offset, bottom, right + mark_offset - mark_length, bottom)
            c.line(right, bottom - mark_offset, right, bottom - mark_offset + mark_length)

    c.showPage()
    c.save()


def process_all_xml():
    input_folder = 'XML Files'
    output_folder = 'Output PDFs'
    os.makedirs(output_folder, exist_ok=True)

    for file_name in os.listdir(input_folder):
        if not file_name.lower().endswith('.xml'):
            continue
        path = os.path.join(input_folder, file_name)
        sections = parse_xml(path)
        if not sections:
            print(f"No sections found in {file_name}")
            continue

        section = sections[0]
        impo = section['printing']['imposition']
        sheet_x = float(impo['sheet_x'])
        sheet_y = float(impo['sheet_y'])

        output_pdf = os.path.join(output_folder,
                                  f"{os.path.splitext(file_name)[0]}_imposed.pdf")
        c = canvas.Canvas(output_pdf)
        draw_imposition_section(c, section, sheet_x, sheet_y)
        print(f"✅ Generated: {output_pdf}")


if __name__ == "__main__":
    process_all_xml()
