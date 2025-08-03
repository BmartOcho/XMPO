from parse_xml import parse_xml

# Load data from XML
sections = parse_xml('XML Files/J208819.xml')

# Compare Finished Size and Imposition Size
for idx, section in enumerate(sections):
    fw = section['finished_width']
    fh = section['finished_height']
    iw = section['impo_width']
    ih = section['impo_height']

    print(f"--- Section {idx+1} ---")
    print(f"Finished: {fw} x {fh}")
    print(f"Imposition: {iw} x {ih}")

    if fw != iw or fh != ih:
        print("\u26a0\ufe0f Mismatch")
    else:
        print("\u2705 Match")

    print()
