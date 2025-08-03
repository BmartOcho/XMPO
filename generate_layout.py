from parse_xml import parse_xml

# Load XML
sections = parse_xml('XML Files/J208819.xml')

# Extract and print layout-related values
for idx, section in enumerate(sections):
    print(f"\n--- Section {idx+1} Layout Info ---")
    
    printing = section['printing']
    impo = printing.get('imposition', {})

    print("Process Front:", printing.get('process_front'))
    print("Process Reverse:", printing.get('process_reverse'))

    print("Number Across (AcrossX):", impo.get('across_x'))
    print("Number Around (AcrossY):", impo.get('across_y'))

    print("Size X:", impo.get('size_x'))
    print("Size Y:", impo.get('size_y'))

    print("Sheet X:", impo.get('sheet_x'))
    print("Sheet Y:", impo.get('sheet_y'))

    print("Printable X:", impo.get('printable_x'))
    print("Printable Y:", impo.get('printable_y'))

    print("Bleed:", impo.get('bleed'))

    print("Grip X1:", impo.get('grip_x1'))
    print("Grip X2:", impo.get('grip_x2'))
    print("Grip Y1:", impo.get('grip_y1'))
    print("Grip Y2:", impo.get('grip_y2'))

    print("Work and Turn:", impo.get('work_turn'))
    print("Work and Tumble:", impo.get('work_tumble'))
