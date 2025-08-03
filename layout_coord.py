from parse_xml import parse_xml

# Load data
sections = parse_xml('XML Files/J208819.xml')

for idx, section in enumerate(sections):
    print(f"\n--- Section {idx+1} Layout Coordinates ---")

    printing = section['printing']
    impo = printing.get('imposition', {})

    # Extract required values
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
    except (TypeError, ValueError):
        print("⚠️ Missing or invalid imposition values.")
        continue

    total_width = across_x * size_x
    total_height = across_y * size_y

    print(f"Total layout size: {total_width:.2f} in x {total_height:.2f} in")
    print(f"Printable area: {printable_x:.2f} in x {printable_y:.2f} in")

    if total_width > printable_x or total_height > printable_y:
        print("❌ Layout exceeds printable area!")
    else:
        print("✅ Layout fits within printable area.")

    print("\nImposition Boxes (x, y, width, height):")
    for row in range(across_y):
        for col in range(across_x):
            x = grip_x1 + col * size_x
            y = grip_y1 + row * size_y
            print(f"Box at ({x:.3f}, {y:.3f}) size {size_x:.3f} x {size_y:.3f}")
