from pathlib import Path
from read_plate import load_reader, read_plates_from_image
from fetch_api import query_vehicle_data

#Konfiguration
IMG_DIR = Path(__file__).resolve().parent / "imgs"
START, END = 1, 10

#Programmet jeg brugte til at teste mit setup og API, før jeg lavede webappen
def main():
    reader = load_reader()

    for i in range(START, END + 1):
        path = IMG_DIR / f"{i}.jpg"
        print(f"\n=== {path} ===")
        try:
            detections = read_plates_from_image(path, reader)
        except FileNotFoundError:
            print(f"[WARN] Could not open {path}")
            continue

        if not detections:
            print("No valid plates found.")
            continue

        for det in detections:
            plate, conf = det["plate"], det["confidence"]
            print(f"Plate: {plate} (conf={conf:.2f}) → querying MotorAPI…")
            info = query_vehicle_data(plate)
            if "vehicle" in info:
                v = info["vehicle"]
                print(f"  Make: {v.get('make')}, Model: {v.get('model')}, Year: {v.get('model_year')}")
            else:
                print(f"  Lookup error: {info.get('vehicle_error')}")

#Kør programmet
if __name__ == "__main__":
    main()
