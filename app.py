import os
import uuid
import threading
from pathlib import Path
from typing import Dict, Any, List

from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename

import cv2
import numpy as np

from read_plate import load_reader, read_plates_from_image
from fetch_api import query_vehicle_data

#Konfiguration
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
UPLOAD_DIR = STATIC_DIR / "uploads"
ANNOTATED_DIR = STATIC_DIR / "annotated"
ALLOWED_EXTS = {"jpg", "jpeg", "png", "bmp", "webp"}
MAX_CONTENT_LENGTH = 12 * 1024 * 1024  # 12 MB

#Sørg for at upload/annotated mapperne findes
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
ANNOTATED_DIR.mkdir(parents=True, exist_ok=True)

#Flask app setup
app = Flask(__name__, static_folder=str(STATIC_DIR), template_folder=str(BASE_DIR / "templates"))
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "dev-secret")  # replace in prod
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

#Load OCR model og lås til threading
READER = load_reader()
OCR_LOCK = threading.Lock()


#Ændre filnavn for at forhindre navnekollisioner
def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTS

#Tegn boks og label på billedet
def draw_box(img, box, label=None):
    box = np.array(box).astype(int)
    cv2.polylines(img, [box], isClosed=True, color=(0, 200, 0), thickness=2)
    if label:
        x, y = box[0]
        cv2.putText(img, label, (x, max(0, y - 6)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 200, 0), 2, cv2.LINE_AA)

#Tegn bokse og gem annoteret billede med unikt navn
def annotate_image(src_path: Path, detections: List[Dict[str, Any]]) -> Path:
    img = cv2.imread(str(src_path))
    if img is None:
        raise FileNotFoundError(f"Cannot read {src_path}")
    for d in detections:
        draw_box(img, d["box"], f"{d['plate']} ({d['confidence']:.2f})")
    stem = src_path.stem
    annotated_name = f"{stem}_{uuid.uuid4().hex[:8]}_annotated.jpg"
    out_path = ANNOTATED_DIR / annotated_name
    cv2.imwrite(str(out_path), img)
    return out_path


#Routes
@app.get("/")
def index():
    return render_template("index.html")

@app.post("/upload")
def upload():
    if "image" not in request.files:
        flash("No file part", "error")
        return redirect(url_for("index"))
    file = request.files["image"]
    if file.filename == "":
        flash("No selected file", "error")
        return redirect(url_for("index"))
    if not allowed_file(file.filename):
        flash("Unsupported file type. Use JPG/PNG/BMP/WEBP.", "error")
        return redirect(url_for("index"))

    filename = secure_filename(file.filename)
    ext = filename.rsplit(".", 1)[1].lower()
    unique_name = f"{Path(filename).stem}_{uuid.uuid4().hex[:8]}.{ext}"
    save_path = UPLOAD_DIR / unique_name
    file.save(str(save_path))

    #Proccesser billede og læs plader
    with OCR_LOCK:
        try:
            detections = read_plates_from_image(save_path, READER)
        except FileNotFoundError:
            flash("Could not read the uploaded image.", "error")
            return redirect(url_for("index"))

    if not detections:
        #Hvis ingen plader fundet, vis originalt billede uden annotation
        return render_template(
            "result.html",
            original_url=url_for("static", filename=f"uploads/{save_path.name}"),
            annotated_url=None,
            results=[],
            no_plates=True,
        )

    #Deduplikér plader, behold den med højeste confidence
    best: Dict[str, Dict[str, Any]] = {}
    for d in detections:
        p = d["plate"]
        if p not in best or d["confidence"] > best[p]["confidence"]:
            best[p] = d
    deduped = list(best.values())

    #Annoter og gem billede med fundne plader
    annotated_path = annotate_image(save_path, deduped)

    #Hent data for hver plade
    results: List[Dict[str, Any]] = []
    for d in deduped:
        plate, conf = d["plate"], d["confidence"]
        info = query_vehicle_data(plate)
        results.append({
            "plate": plate,
            "confidence": round(float(conf), 3),
            "vehicle": info.get("vehicle"),
            "environment": info.get("environment"),
            "equipment": info.get("equipment"),
            "errors": {
                "vehicle": info.get("vehicle_error"),
                "environment": info.get("env_error"),
                "equipment": info.get("equip_error"),
            }
        })

    return render_template(
        "result.html",
        original_url=url_for("static", filename=f"uploads/{save_path.name}"),
        annotated_url=url_for("static", filename=f"annotated/{annotated_path.name}"),
        results=results,
        no_plates=False,
    )


if __name__ == "__main__":
    #Kør Flask app
    app.run(host="0.0.0.0", port=5000, debug=True)
