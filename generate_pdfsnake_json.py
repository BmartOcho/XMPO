import os
import json
import subprocess
from parse_xml import parse_xml

PDFSNAKE_PATH = "pdfsnake"  # Adjust if pdfsnake command path differs
INPUT_FOLDER = "XML Files"
OUTPUT_JSON_FOLDER = "PDFSnake_JSON"
OUTPUT_PDF_FOLDER = "PDFSnake_Output"
PDF_FOLDER = "PDFs"  # Folder containing original PDFs (named to match job key)

os.makedirs(OUTPUT_JSON_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_PDF_FOLDER, exist_ok=True)


def inches_to_points(inches):
    return round(float(inches) * 72, 2)


def generate_json_config(xml_data, job_name, impo_type):
    printing = xml_data['printing']
    impo = printing['imposition']

    config = {
        "type": impo_type,
        "input": os.path.join(PDF_FOLDER, f"{job_name}_1.pdf"),
        "output": os.path.join(OUTPUT_PDF_FOLDER, f"{job_name}_imposed.pdf"),
        "paperWidth": inches_to_points(impo['sheet_x']),
        "paperHeight": inches_to_points(impo['sheet_y']),
        "leftMargin": inches_to_points(impo.get('grip_x1', 0.25)),
        "topMargin": inches_to_points(impo.get('grip_y1', 0.375)),
        "verticalGutterWidth": 0,
        "horizontalGutterWidth": 0,
        "bleeds": {
            "top": inches_to_points(impo.get('bleed', 0)),
            "bottom": inches_to_points(impo.get('bleed', 0)),
            "left": inches_to_points(impo.get('bleed', 0)),
            "right": inches_to_points(impo.get('bleed', 0))
        },
        "lineDistance": inches_to_points(0.0625),
        "lineLength": inches_to_points(0.125),
        "lineThickness": 1.5,
        "cropMarks": True
    }

    return config


def process_all_xml():
    for file in os.listdir(INPUT_FOLDER):
        if not file.lower().endswith(".xml"):
            continue

        xml_path = os.path.join(INPUT_FOLDER, file)
        sections = parse_xml(xml_path)
        if not sections:
            print(f"Skipping {file}: no sections found.")
            continue

        section = sections[0]
        number_up = int(section['printing'].get('number_up', 0))
        job_key = section.get('key', os.path.splitext(file)[0])

        # Rule: odd NumberUp => monkey
        impo_type = "monkey" if number_up % 2 != 0 else "step_and_repeat"

        config = generate_json_config(section, job_key, impo_type)
        json_path = os.path.join(OUTPUT_JSON_FOLDER, f"{job_key}.json")

        with open(json_path, 'w') as jf:
            json.dump(config, jf, indent=2)

        print(f"✅ JSON generated for {job_key}: {json_path}")

        # Run PDF Snake CLI
        try:
            subprocess.run([PDFSNAKE_PATH, json_path], check=True)
            print(f"🎉 PDF generated: {config['output']}")
        except subprocess.CalledProcessError as e:
            print(f"❌ PDFSnake failed for {job_key}: {e}")


if __name__ == "__main__":
    process_all_xml()
