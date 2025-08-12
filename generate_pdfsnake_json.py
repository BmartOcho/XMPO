import os
import json
import subprocess
from parse_xml import parse_xml

PDFSNAKE_CMD = "pdfsnake"  # or full path to CLI tool
INPUT_FOLDER = "XML Files"
OUTPUT_JSON = "PDFSnake_JSON"
INPUT_PDF_FOLDER = "PDFs"
OUTPUT_PDF_FOLDER = "PDFSnake_Output"

os.makedirs(OUTPUT_JSON, exist_ok=True)
os.makedirs(OUTPUT_PDF_FOLDER, exist_ok=True)

def inches_to_points(inch):
    return inch * 72

def generate_config(xml_data, job_name, impo_type):
    impo = xml_data['printing']['imposition']
    return {
        "paperWidth": inches_to_points(impo['sheet_x']),
        "paperHeight": inches_to_points(impo['sheet_y']),
        "leftMargin": inches_to_points(impo['grip_x1']),
        "topMargin": inches_to_points(impo['grip_y1']),
        "croppedBleed": inches_to_points(impo['bleed']),
        # Additional PDF Snake options can be set here
    }

def process_all():
    for xml_file in os.listdir(INPUT_FOLDER):
        if not xml_file.lower().endswith('.xml'):
            continue
        xml_path = os.path.join(INPUT_FOLDER, xml_file)
        sections = parse_xml(xml_path)
        if not sections:
            continue

        section = sections[0]
        number_up = int(section['printing'].get('number_up', 0))
        impo_type = "monkey" if number_up % 2 != 0 else "step_and_repeat"
        job_key = section.get('key', os.path.splitext(xml_file)[0])

        config = generate_config(section, job_key, impo_type)
        config_path = os.path.join(OUTPUT_JSON, f"{job_key}.json")
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

        print(f"JSON ready: {config_path}")

        pdf_input = os.path.join(INPUT_PDF_FOLDER, f"{job_key}_1.pdf")
        if not os.path.isfile(pdf_input):
            print(f" Input PDF not found: {pdf_input}")
            continue

        output_pdf = os.path.join(OUTPUT_PDF_FOLDER, f"{job_key}_imposed.pdf")
        cmd = [
            PDFSNAKE_CMD, "impose",
            "-j", config_path,
            pdf_input
        ]
        try:
            subprocess.run(cmd, check=True)
            print(f" Generated PDF: {output_pdf}")
        except subprocess.CalledProcessError as e:
            print(f" PDF Snake error: {e}")

if __name__ == "__main__":
    process_all()
