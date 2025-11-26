# test_images_batch.py
import sys
from pathlib import Path
import cv2
from ultralytics import YOLO

# ---------- CONFIG ----------
MODEL_PATH = r"best.pt"
OUT_DIR = r"batch_results"
CONF = 0.45
# ---------- END CONFIG ----------

def process_image_folder(model, input_dir):
    inp = Path(input_dir)
    out = Path(OUT_DIR)
    out.mkdir(parents=True, exist_ok=True)

    images = sorted([p for p in inp.glob("*") if p.suffix.lower() in [".jpg", ".jpeg", ".png"]])
    if not images:
        print("No images found in", inp)
        return

    print(f"Running inference on {len(images)} images...")
    for p in images:
        results = model.predict(source=str(p), conf=CONF)
        r = results[0]
        annotated = r.plot()
        out_path = out / p.name
        cv2.imwrite(str(out_path), annotated)

        labels = [r.names[int(c)] for c in r.boxes.cls] if len(r.boxes) else []
        print(f"{p.name} -> {len(labels)} objects, classes: {labels}")

    print("Saved annotated images to:", out.resolve())


def process_camera(model, cam_id):
    print(f"Opening webcam {cam_id}...")
    cap = cv2.VideoCapture(cam_id)

    if not cap.isOpened():
        print("❌ Could not open webcam:", cam_id)
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to grab frame")
            break

        results = model.predict(frame, conf=CONF)
        annotated = results[0].plot()

        cv2.imshow("Webcam Detection", annotated)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Exiting...")
            break

    cap.release()
    cv2.destroyAllWindows()


def process_video(model, video_path):
    print("Processing video:", video_path)
    results = model.predict(source=video_path, conf=CONF, show=True)
    # YOLO automatically shows & processes video
    print("Finished video processing.")


def main():
    model = YOLO(MODEL_PATH)

    if len(sys.argv) < 2:
        print("Usage:")
        print(" python test_images_batch.py folder=<path>")
        print(" python test_images_batch.py webcam=0")
        print(" python test_images_batch.py video=<path>")
        sys.exit(1)

    arg = sys.argv[1]

    # FOLDER MODE
    if arg.startswith("folder="):
        folder_path = arg.split("=", 1)[1]
        process_image_folder(model, folder_path)
        return

    # WEBCAM MODE
    if arg.startswith("webcam="):
        cam_id = arg.split("=", 1)[1]
        process_camera(model, cam_id)
        return

    # VIDEO MODE
    if arg.startswith("video="):
        video_path = arg.split("=", 1)[1]
        process_video(model, video_path)
        return

    print("❌ Invalid argument. Use:")
    print(" folder=<path> | webcam=0 | video=<path>")


if __name__ == "__main__":
    main()
