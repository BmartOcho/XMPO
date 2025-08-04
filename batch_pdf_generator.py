import os
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from parse_xml import parse_xml


def draw_imposition_section(c, section, sheet_x, sheet_y):
    """
    Draw a single section imposition onto the canvas `c`.
    Marks trimmed cards offset by bleed and half-bleed, with crop marks offset by 0.0625".
    """
    printing = section['printing']
    impo = printing.get('imposition', {})

    # Grid counts
    across = int(impo.get('across_x', 0))
    down = int(impo.get('across_y', 0))
    # Full layout cell size including bleed
    size_x = float(impo.get('size_x', 0))
    size_y = float(impo.get('size_y', 0))
    # Printable area on the sheet
    printable_x = float(impo.get('printable_x', sheet_x))
    printable_y = float(impo.get('printable_y', sheet_y))

    # Finished (trimmed) card size from XML
    finished_w = float(impo.get('finished_width', 0))
    finished_h = float(impo.get('finished_height', 0))
    # Bleed amount on each side
    bleed = float(impo.get('bleed', 0))
    # Compute bleed offsets dynamically (half of extra)
    bleed_x = (size_x - finished_w) / 2.0
    bleed_y = (size_y - finished_h) / 2.0

    # Center full block (including bleed) in printable area
    total_w = across * size_x
    total_h = down * size_y
    offset_x = (printable_x - total_w) / 2.0 + (sheet_x - printable_x) / 2.0
    offset_y = (printable_y - total_h) / 2.0 + (sheet_y - printable_y) / 2.0

    # Setup canvas
    c.setPageSize((sheet_x * inch, sheet_y * inch))
    c.setLineWidth(1.5)  # 1.5 points thickness
    c.setStrokeColorRGB(0, 0, 0)

    # Crop marks parameters
    mark_offset = 0.0625 * inch  # 1/16" from trim edge
    mark_length = 0.25 * inch    # 1/4" long

    # Draw each cell
    for row in range(down):
        for col in range(across):
            # Compute trim-box bottom-left in PDF coords (bottom-left origin)
            trim_x = (offset_x + col * size_x + bleed_x) * inch
            trim_y = (offset_y + row * size_y + bleed_y) * inch
            # Coordinates of trim edges
            left = trim_x
            bottom = trim_y
            right = left + finished_w * inch
            top = bottom + finished_h * inch

            # Top-left crop marks
            # Horizontal (to the right)
            c.line(left - mark_offset, top + mark_offset,
                   left - mark_offset + mark_length, top + mark_offset)
            # Vertical (downward)
            c.line(left - mark_offset, top + mark_offset,
                   left - mark_offset, top + mark_offset - mark_length)

            # Top-right crop marks
            c.line(right + mark_offset, top + mark_offset,
                   right + mark_offset - mark_length, top + mark_offset)
            c.line(right + mark_offset, top + mark_offset,
                   right + mark_offset, top + mark_offset - mark_length)

            # Bottom-left crop marks
            c.line(left - mark_offset, bottom - mark_offset,
                   left - mark_offset + mark_length, bottom - mark_offset)
            c.line(left - mark_offset, bottom - mark_offset,
                   left - mark_offset, bottom - mark_offset + mark_length)

            # Bottom-right crop marks
            c.line(right + mark_offset, bottom - mark_offset,
                   right + mark_offset - mark_length, bottom - mark_offset)
            c.line(right + mark_offset, bottom - mark_offset,
                   right + mark_offset, bottom - mark_offset + mark_length)

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

        # Only first section for now
        section = sections[0]
        impo = section['printing']['imposition']
        sheet_x = float(impo['sheet_x'])
        sheet_y = float(impo['sheet_y'])

        output_pdf = os.path.join(
            output_folder,
            f"{os.path.splitext(file_name)[0]}_imposed.pdf"
        )
        c = canvas.Canvas(output_pdf)
        draw_imposition_section(c, section, sheet_x, sheet_y)
        print(f"✅ Generated: {output_pdf}")


if __name__ == "__main__":
    process_all_xml()
