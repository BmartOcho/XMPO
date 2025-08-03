import matplotlib.pyplot as plt
from parse_xml import parse_xml
import sys
import os

# Load all XML files in the folder
folder_path = "XML Files"
xml_files = [f for f in os.listdir(folder_path) if f.endswith('.xml')]

for file in xml_files:
    xml_path = os.path.join(folder_path, file)
    print(f"\nPreviewing: {file}")

    sections = parse_xml(xml_path)

    for idx, section in enumerate(sections):
        printing = section['printing']
        impo = printing.get('imposition', {})

        try:
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
        except (TypeError, ValueError):
            print("⚠️ Skipping section due to invalid values.")
            continue

        total_width = across_x * size_x
        total_height = across_y * size_y

        # Calculate offsets to center layout
        offset_x = (printable_x - total_width) / 2
        offset_y = (printable_y - total_height) / 2

        fig, ax = plt.subplots(figsize=(10, 8))
        ax.set_title(f"Imposition Preview - {file} - Section {idx+1}")
        ax.set_xlim(0, sheet_x)
        ax.set_ylim(0, sheet_y)
        ax.set_aspect('equal')
        ax.invert_yaxis()

        # Draw non-printable area
        if printable_x < sheet_x or printable_y < sheet_y:
            left_margin = (sheet_x - printable_x) / 2
            top_margin = (sheet_y - printable_y) / 2
            ax.add_patch(plt.Rectangle((0, 0), sheet_x, sheet_y, color='red', alpha=0.2))
            ax.add_patch(plt.Rectangle((left_margin, top_margin), printable_x, printable_y, color='white'))

        # Crop mark settings
        crop_offset = 0.0625  # inches
        crop_length = 0.125   # inches
        crop_thickness = 1.5 / 72  # convert points to inches (1 pt = 1/72 in)

        # Draw imposition boxes
        for row in range(across_y):
            for col in range(across_x):
                x = offset_x + col * size_x + (sheet_x - printable_x) / 2
                y = offset_y + row * size_y + (sheet_y - printable_y) / 2

                # Draw artwork area
                artwork = plt.Rectangle((x, y), size_x, size_y, linewidth=1, edgecolor='blue', facecolor='lightblue')
                ax.add_patch(artwork)

                # Draw bleed box
                bleed_box = plt.Rectangle(
                    (x + bleed, y + bleed),
                    size_x - 2 * bleed,
                    size_y - 2 * bleed,
                    linewidth=0.5,
                    edgecolor='red',
                    facecolor='none',
                    linestyle='--'
                )
                ax.add_patch(bleed_box)

                # Draw crop marks at each corner
                for dx in [0, size_x]:
                    for dy in [0, size_y]:
                        cx = x + dx
                        cy = y + dy

                        # Horizontal crop mark
                        ax.plot([
                            cx - crop_length if dx else cx + crop_length,
                            cx
                        ], [cy - crop_offset if dy else cy + crop_offset] * 2, color='black', linewidth=crop_thickness)

                        # Vertical crop mark
                        ax.plot([cx - crop_offset if dx else cx + crop_offset] * 2, [
                            cy - crop_length if dy else cy + crop_length,
                            cy
                        ], color='black', linewidth=crop_thickness)

        # Draw printable area border
        printable_border = plt.Rectangle(
            ((sheet_x - printable_x) / 2, (sheet_y - printable_y) / 2),
            printable_x, printable_y,
            linewidth=1.5, edgecolor='black', facecolor='none'
        )
        ax.add_patch(printable_border)

        plt.xlabel("Width (in)")
        plt.ylabel("Height (in)")
        plt.grid(True)
        plt.tight_layout()
        plt.show()
