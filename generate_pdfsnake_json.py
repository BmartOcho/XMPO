# generate_pdfsnake_json.py
import os
import json
import glob
import shutil
import subprocess
from pathlib import Path
import xml.etree.ElementTree as ET

# ---- Paths / CLI ----
PDFSNAKE_CMD = "pdfsnake"  # or absolute path to the CLI
INPUT_FOLDER = "XML Files"            # printIQ job XML lives here
INPUT_PDF_FOLDER = "PDFs"             # expects {JobNumber}_1.pdf
OUTPUT_JSON = "PDFSnake_JSON"         # writes {JobNumber}.json here
OUTPUT_PDF_FOLDER = "PDFSnake_Output" # final imposed PDFs end up here

Path(OUTPUT_JSON).mkdir(parents=True, exist_ok=True)
Path(OUTPUT_PDF_FOLDER).mkdir(parents=True, exist_ok=True)

# ---- Helpers ----
def inches_to_points(val, default=0.0):
    """Accept str/int/float inches. Return float points (72 pt/inch)."""
    try:
        return float(val) * 72.0
    except (TypeError, ValueError):
        return float(default) * 72.0

def get_text(root, xpath, default=None):
    el = root.find(xpath)
    return el.text.strip() if (el is not None and el.text is not None) else default

def get_float(root, xpath, default=None):
    t = get_text(root, xpath, None)
    if t is None or t == "":
        return default
    try:
        return float(t)
    except ValueError:
        return default

def parse_job_fields(xml_path: str) -> dict:
    """
    Extract fields needed for PDF Snake from the printIQ XML.
    Returns inches (not yet converted) and JobNumber.
    """
    root = ET.parse(xml_path).getroot()

    job_number = get_text(root, "./JobNumber") or Path(xml_path).stem

    # Sheet size (inches)
    sheet_w_in = get_float(root, ".//Printing/SheetWidth", 0.0)
    sheet_h_in = get_float(root, ".//Printing/SheetDepth", 0.0)

    # Grips / Bleed (inches)
    grip_x1_in = get_float(root, ".//Imposition/GripX1", 0.0)
    grip_y1_in = get_float(root, ".//Imposition/GripY1", 0.0)
    bleed_in   = get_float(root, ".//Imposition/Bleed",  0.125)  # default 1/8"

    # Duplex? If reverse process text exists, treat as duplex
    process_reverse = (get_text(root, ".//Printing/ProcessReverse", "") or "").strip()
    double_sided = bool(process_reverse)

    return {
        "job_number": job_number,
        "sheet_w_in": sheet_w_in,
        "sheet_h_in": sheet_h_in,
        "grip_x1_in": grip_x1_in,
        "grip_y1_in": grip_y1_in,
        "bleed_in":   bleed_in,
        "double_sided": double_sided,
    }

def make_pdfsnake_payload_from_job(job: dict) -> dict:
    """
    Build the exact JSON structure PDF Snake CLI expects (mirrors Monkey.json).
    All numeric values in points.
    """
    paper_width_pt  = inches_to_points(job["sheet_w_in"])
    paper_height_pt = inches_to_points(job["sheet_h_in"])
    left_margin_pt  = inches_to_points(job["grip_x1_in"])
    top_margin_pt   = inches_to_points(job["grip_y1_in"])
    bleed_pt        = inches_to_points(job["bleed_in"])

    # Match your Monkey.json defaults
    vertical_gutter_pt   = inches_to_points(0.25)
    horizontal_gutter_pt = inches_to_points(0.25)
    line_length_pt       = inches_to_points(0.10)   # 7.2 pt
    line_thickness_pt    = inches_to_points(0.01)   # 0.72 pt
    line_distance_pt     = inches_to_points(0.07)   # 5.04 pt

    step = {
        "paperWidth": paper_width_pt,
        "paperHeight": paper_height_pt,
        "leftMargin": left_margin_pt,
        "topMargin": top_margin_pt,
        "verticalGutterWidth": vertical_gutter_pt,
        "horizontalGutterWidth": horizontal_gutter_pt,
        "center": True,
        "pageOrder": "stepAndRepeat",
        "doubleSided": bool(job["double_sided"]),
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
        "kind": "Monkey",
    }

    return {"steps": [step]}

def write_payload(out_path: str, payload: dict) -> None:
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

def find_input_pdf(job_number: str, pdf_folder: str) -> str | None:
    """
    Find the input PDF that matches the <JobNumber> rule.
    Expected naming: {JobNumber}_1.pdf in PDFs/ (case-insensitive).
    """
    expected_name = f"{job_number}_1.pdf".lower()
    folder = Path(pdf_folder)
    if not folder.exists():
        return None

    for p in folder.iterdir():
        if p.is_file() and p.name.lower() == expected_name:
            return str(p)
    return None

def run_pdfsnake_impose(config_path: str, input_pdf: str) -> str | None:
    """
    Call pdfsnake impose and return the path to the generated PDF.
    The CLI writes beside the input as '*-pdfsnake*.pdf' — capture and move later.
    """
    cmd = [PDFSNAKE_CMD, "impose", "-j", config_path, input_pdf]
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f" PDF Snake error: {e}")
        return None

    base = os.path.splitext(os.path.basename(input_pdf))[0]
    parent = os.path.dirname(input_pdf) or "."
    candidates = sorted(
        glob.glob(os.path.join(parent, f"{base}-pdfsnake*.pdf")),
        key=os.path.getmtime,
        reverse=True,
    )
    return candidates[0] if candidates else None

def process_all():
    xml_files = [p for p in os.listdir(INPUT_FOLDER) if p.lower().endswith(".xml")]
    if not xml_files:
        print(f"No XML files found in '{INPUT_FOLDER}'.")
        return

    for xml_name in xml_files:
        xml_path = os.path.join(INPUT_FOLDER, xml_name)

        # --- Parse job XML ---
        try:
            job = parse_job_fields(xml_path)
        except Exception as e:
            print(f" Failed to parse XML '{xml_name}': {e}")
            continue

        job_number = job["job_number"]

        # --- Build and write PDFSnake JSON payload ---
        payload = make_pdfsnake_payload_from_job(job)
        out_json = os.path.join(OUTPUT_JSON, f"{job_number}.json")
        write_payload(out_json, payload)
        print(f"JSON ready: {out_json}")

        # --- Find required input PDF strictly by <JobNumber>_1.pdf ---
        input_pdf = find_input_pdf(job_number, INPUT_PDF_FOLDER)
        if not input_pdf:
            print(f" Input PDF not found: {Path(INPUT_PDF_FOLDER) / (job_number + '_1.pdf')}")
            continue

        # --- Run CLI and stash result in OUTPUT_PDF_FOLDER ---
        generated = run_pdfsnake_impose(out_json, input_pdf)
        if generated and os.path.isfile(generated):
            target = os.path.join(OUTPUT_PDF_FOLDER, f"{job_number}_imposed.pdf")
            try:
                shutil.move(generated, target)
                print(f" Generated PDF: {target}")
            except Exception as move_err:
                print(f" Could not move output ({generated}): {move_err}")
        else:
            print(" No imposed PDF found after running PDF Snake.")

if __name__ == "__main__":
    process_all()
