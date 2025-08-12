import os
import json
import glob
import shutil
import subprocess
from pathlib import Path
from parse_xml import parse_xml

PDFSNAKE_CMD = "pdfsnake"  # or full path to CLI tool
INPUT_FOLDER = "XML Files"
OUTPUT_JSON = "PDFSnake_JSON"
INPUT_PDF_FOLDER = "PDFs"
OUTPUT_PDF_FOLDER = "PDFSnake_Output"

os.makedirs(OUTPUT_JSON, exist_ok=True)
os.makedirs(OUTPUT_PDF_FOLDER, exist_ok=True)

def inches_to_points(inch_val):
    """
    Accepts str/int/float inches. Returns float points (1 in = 72 pt).
    Avoids string concatenation bugs ("13" + "13" -> "1313").
    """
    try:
        return float(inch_val) * 72.0
    except (TypeError, ValueError):
        return 0.0

def build_pdfsnake_steps(xml_section, job_name: str):
    """
    Build the exact JSON structure PDF Snake CLI expects:
    { "steps": [ { ...step fields... } ] }
    Fields mirror your provided 'Monkey.json' sample.
    """
    printing = xml_section.get("printing", {})
    impo = printing.get("imposition", {}) or {}

    paper_w_pt = inches_to_points(impo.get("sheet_x", 0))
    paper_h_pt = inches_to_points(impo.get("sheet_y", 0))
    left_margin_pt = inches_to_points(impo.get("grip_x1", 0))
    top_margin_pt = inches_to_points(impo.get("grip_y1", 0))
    bleed_pt = inches_to_points(impo.get("bleed", 0))

    # Reasonable defaults (match your good sample)
    vertical_gutter_pt = inches_to_points(0.25)
    horizontal_gutter_pt = inches_to_points(0.25)
    line_length_pt = inches_to_points(0.10)     # 7.2 pt
    line_thickness_pt = inches_to_points(0.01)  # 0.72 pt
    line_distance_pt = inches_to_points(0.07)   # 5.04 pt

    step = {
        "paperWidth": paper_w_pt,
        "paperHeight": paper_h_pt,
        "leftMargin": left_margin_pt,
        "topMargin": top_margin_pt,
        "verticalGutterWidth": vertical_gutter_pt,
        "horizontalGutterWidth": horizontal_gutter_pt,
        "center": True,
        "pageOrder": "stepAndRepeat",
        "doubleSided": True,
        "repeat": 1,
        "newStackOrder": True,
        "cropMarks": True,
        "marksInGutters": True,
        "centerMarks": True,
        "lineLength": line_length_pt,
        "lineThickness": line_thickness_pt,
        "lineDistance": line_distance_pt,
        "fourColorBlack": False,
        "whiteBorder": False,
        "bleeds": "pullFromDoc",
        "fixedBleedLeft": bleed_pt,
        "fixedBleedTop": bleed_pt,
        "direction": "leftToRight",
        # PDF Snake uses "kind" to indicate tool; your sample used "Monkey".
        # If you want to vary this based on XML, swap this out.
        "kind": "Monkey"
    }

    return {"steps": [step]}

def impose_with_pdfsnake(config_path: str, input_pdf: str) -> str | None:
    """
    Runs pdfsnake impose. The CLI writes the output next to input as '*-pdfsnake*.pdf'.
    Returns the path to the generated file if found, else None.
    """
    cmd = [PDFSNAKE_CMD, "impose", "-j", config_path, input_pdf]
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f" PDF Snake error: {e}")
        return None

    # Find the newest file that matches the CLI's naming convention
    base = os.path.splitext(os.path.basename(input_pdf))[0]
    parent = os.path.dirname(input_pdf) or "."
    candidates = sorted(
        glob.glob(os.path.join(parent, f"{base}-pdfsnake*.pdf")),
        key=os.path.getmtime,
        reverse=True
    )
    return candidates[0] if candidates else None

def process_all():
    for xml_file in os.listdir(INPUT_FOLDER):
        if not xml_file.lower().endswith(".xml"):
            continue

        xml_path = os.path.join(INPUT_FOLDER, xml_file)
        sections = parse_xml(xml_path)
        if not sections:
            print(f" Skipping (no sections parsed): {xml_file}")
            continue

        section = sections[0]
        job_key = section.get("key", os.path.splitext(xml_file)[0])

        # Build correct JSON structure
        payload = build_pdfsnake_steps(section, job_key)
        config_path = os.path.join(OUTPUT_JSON, f"{job_key}.json")
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        print(f"JSON ready: {config_path}")

        # Input PDF
        pdf_input = os.path.join(INPUT_PDF_FOLDER, f"{job_key}_1.pdf")
        if not os.path.isfile(pdf_input):
            print(f" Input PDF not found: {pdf_input}")
            continue

        # Run CLI, then move the generated file into OUTPUT_PDF_FOLDER
        generated = impose_with_pdfsnake(config_path, pdf_input)
        if generated and os.path.isfile(generated):
            out_pdf = os.path.join(OUTPUT_PDF_FOLDER, f"{job_key}_imposed.pdf")
            try:
                shutil.move(generated, out_pdf)
                print(f" Generated PDF: {out_pdf}")
            except Exception as move_err:
                print(f" Could not move output ({generated}): {move_err}")
        else:
            print(" No imposed PDF found after running PDF Snake.")

if __name__ == "__main__":
    process_all()
