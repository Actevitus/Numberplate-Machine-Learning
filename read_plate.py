import re
import cv2
import numpy as np
import easyocr
from pathlib import Path
from typing import List, Tuple, Dict

#Variabel der beslutter hvor "sikker" machinelearning modellen skal være før den accepterer et resultat
CONF_THRESH = 0.4

#Rens og normaliser tekst
def normalize_plate(text: str) -> str:
    t = text.strip().upper()
    t = re.sub(r"[ \-\.\:]", "", t)
    if "O" in t and any(ch.isdigit() for ch in t):
        t = t.replace("O", "0")
    return t

#Tjek om teksten ligner et dansk nummerplade format
def looks_like_dk_plate(cleaned: str) -> bool:
    return len(cleaned) == 7 and cleaned[:2].isalpha() and cleaned[2:].isdigit()

#Læs nummerplader fra et billede
def read_plates_from_image(path: Path, reader: easyocr.Reader) -> List[Dict]:
    img = cv2.imread(str(path))
    if img is None:
        raise FileNotFoundError(f"Cannot read {path}")

    results = reader.readtext(img)
    found = []
    for box, text, conf in results:
        if conf < CONF_THRESH:
            continue
        cleaned = normalize_plate(text)
        if looks_like_dk_plate(cleaned):
            found.append({
                "plate": cleaned,
                "confidence": float(conf),
                "box": box
            })
    return found

#Opret og genbrug EasyOCR reader
def load_reader() -> easyocr.Reader:
    return easyocr.Reader(["en"], gpu=False)