import json, glob
bad=[]
for p in glob.glob("PDFSnake_JSON/*.json"):
    try:
        with open(p, "r", encoding="utf-8") as f:
            data=json.load(f)
        if "steps" not in data or not isinstance(data["steps"], list):
            bad.append(p)
    except Exception as e:
        bad.append(f"{p} (parse error: {e})")
print("Missing/invalid:", *bad, sep="\n")
