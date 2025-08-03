from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from parse_xml import parse_xml

def draw_imposition_section(c, section, xml_filename, out_filename):
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
    sheet_x = float(impo.get('sheet_x'))
    sheet_y = float(impo.get('sheet_y'))

    total_width = across_x * size_x
    total_height = across_y * size_y

    offset_x = (printable_x - total_width) / 2 + (sheet_x - printable_x) / 2
    offset_y = (printable_y - total_height) / 2 + (sheet_y - printable_y) / 2

    c.setPageSize((sheet_x * inch, sheet_y * inch))

    # Draw the impositions with bleed/trim
    for row in range(across_y):
        for col in range(across_x):
            x = (offset_x + col * size_x) * inch
            y = (sheet_y - (offset_y + row * size_y + size_y)) * inch  # invert origin

            # Trim box (solid black)
            c.setLineWidth(1.5)
            c.setStrokeColorRGB(0, 0, 0)

            # Top-left corner trim mark
            cx, cy = x, y + size_y * inch
            c.line(cx - 0.0625 * inch, cy, cx, cy)
            c.line(cx, cy + 0.0625 * inch, cx, cy)
            # Other corners similarly:
            # Top-right
            cx2 = x + size_x * inch
            c.line(cx2, cy, cx2 + 0.0625 * inch, cy)
            c.line(cx2, cy + 0.0625 * inch, cx2, cy)
            # Bottom-left
            bx, by = x, y
            c.line(bx - 0.0625 * inch, by, bx, by)
            c.line(bx, by - 0.0625 * inch, bx, by)
            # Bottom-right
            brx, bry = bx + size_x * inch, by
            c.line(brx, bry, brx + 0.0625 * inch, bry)
            c.line(brx, bry - 0.0625 * inch, brx, bry)

    c.showPage()
    c.save()
    print(f"PDF saved to: {out_filename}")

if __name__ == "__main__":
    sections = parse_xml('XML Files/J208819.xml')
    if not sections:
        print("No sections found.")
    else:
        draw_imposition_section(
            canvas.Canvas("imposition_output.pdf"),
            sections[0],
            "J208819.xml",
            "imposition_output.pdf"
        )
