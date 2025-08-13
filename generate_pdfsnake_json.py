# generate_pdfsnake_json.py
import os
import json
import glob
import shutil
import subprocess
from pathlib import Path
import xml.etree.ElementTree as ET

# ---- Paths / CLI ----
PDFSNAKE_CMD = "pdfsnake"             # or absolute path to the CLI
INPUT_PDF_FOLDER = "PDFs"             # scan PDFs here
INPUT_JOB_FOLDER = "XML Files"        # expects {JobNumber}.xml (or .json that contains XML)
OUTPUT_JSON = "PDFSnake_JSON"         # writes {JobNumber}.json here
OUTPUT_PDF_FOLDER = "PDFSnake_Output" # final imposed PDFs end up here

Path(OUTPUT_JSON).mkdir(parents=True, exist_ok=True)
Path(OUTPUT_PDF_FOLDER).mkdir(parents=True, exist_ok=True)

# ---- Utilities ----
def inches_to_points(val, default=0.0):
    """Accept str/int/float inches. Return float points (72 pt/inch)."""
    try:
        return float(val) * 72.0
    except (TypeError, ValueError):
        return float(default) * 72.0

def safe_text(el, default=None):
    return el.text.strip() if (el is not None and el.text is not None) else default

def get_text(root, xpath, default=None):
    return safe_text(root.find(xpath), default)

def get_float(root, xpath, default=None):
    t = get_text(root, xpath, None)
    if t is None or t == "":
        return default
    try:
        return float(t)
    except ValueError:
        return default

def case_insensitive_find(folder: str, filename_no_ext: str, exts: tuple[str, ...]) -> str | None:
    """
    Find a file whose base name matches filename_no_ext (case-insensitive) with one of the given extensions.
    Returns the first match path or None.
    """
    folder_p = Path(folder)
    if not folder_p.exists():
        return None
    targets = {f"{filename_no_ext}{ext}".lower() for ext in exts}
    for p in folder_p.iterdir():
        if p.is_file() and p.name.lower() in targets:
            return str(p)
    return None

def parse_job_fields_from_xmllike(path: str) -> dict:
    """
    Parse 'printIQ-like' XML. Some shops export XML with .json extension;
    if the file begins with '<', we parse it as XML anyway.
    Returns inches (not yet converted) and JobNumber.
    """
    text = Path(path).read_text(encoding="utf-8", errors="ignore").lstrip()
    if not text.startswith("<"):
        raise ValueError(f"File does not appear to be XML: {path}")

    root = ET.fromstring(text)

    job_number = get_text(root, "./JobNumber") or Path(path).stem

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

def run_pdfsnake_impose(config_path: str, input_pdf: str) -> str | None:
    """
    Call pdfsnake impose and return the path to the generated PDF.
    The CLI writes beside the input as '*-pdfsnake*.pdf' — capture and move later.
    """
    cmd = [PDFSNAKE_CMD, "impose", "-j", config_path, input_pdf]
    try:
        # Let pdfsnake print its own "Reading..." / "Wrote..." lines
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

# ---- Main flow ----
def process_all():
    pdf_dir = Path(INPUT_PDF_FOLDER)
    if not pdf_dir.exists():
        print(f"No 'PDFs' folder found at: {pdf_dir.resolve()}")
        return

    # Gather PDFs (case-insensitive .pdf)
    pdf_paths = [p for p in pdf_dir.iterdir() if p.is_file() and p.suffix.lower() == ".pdf"]
    if not pdf_paths:
        print(f"No PDFs found in '{INPUT_PDF_FOLDER}'.")
        return

    processed = 0
    missing_job_meta = []
    missing_output = []
    errors = []

    for pdf_path in sorted(pdf_paths):
        base = pdf_path.stem  # e.g., "J212991-02_1"
        job_number = base.split("_", 1)[0]  # part before first underscore

        # Find job XML (or .json that actually contains XML) by job_number
        job_meta_path = case_insensitive_find(INPUT_JOB_FOLDER, job_number, (".xml", ".XML", ".json", ".JSON"))
        if not job_meta_path:
            print(f" Job XML/JSON not found for {job_number} (needed for {pdf_path.name})")
            missing_job_meta.append(pdf_path.name)
            continue

        # Parse the job fields from the XML-like file
        try:
            job = parse_job_fields_from_xmllike(job_meta_path)
        except Exception as e:
            msg = f" Failed to parse job meta '{Path(job_meta_path).name}' for {pdf_path.name}: {e}"
            print(msg)
            errors.append(msg)
            continue

        # Build and write PDFSnake JSON payload (by job number, one per job spec)
        payload = make_pdfsnake_payload_from_job(job)
        out_json = os.path.join(OUTPUT_JSON, f"{job['job_number']}.json")
        write_payload(out_json, payload)
        print(f"JSON ready: {out_json}")

        # Run pdfsnake impose for THIS input PDF
        generated = run_pdfsnake_impose(out_json, str(pdf_path))
        if generated and os.path.isfile(generated):
            target = os.path.join(OUTPUT_PDF_FOLDER, f"{pdf_path.stem}_imposed.pdf")
            try:
                shutil.move(generated, target)
                print(f" Generated PDF: {target}")
                processed += 1
            except Exception as move_err:
                msg = f" Could not move output ({generated}): {move_err}"
                print(msg)
                errors.append(msg)
        else:
            print(f" No imposed PDF written for {pdf_path.name}.")
            missing_output.append(pdf_path.name)

    # Summary
    print("\n--- Summary ---")
    print(f"Processed OK: {processed}")
    if missing_job_meta:
        print(f"Missing job XML/JSON for: {', '.join(missing_job_meta)}")
    if missing_output:
        print(f"No output written for: {', '.join(missing_output)}")
    if errors:
        print("Errors:")
        for e in errors:
            print(f" - {e}")

if __name__ == "__main__":
    process_all()
