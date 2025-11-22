import cv2
import sys
import os

def main():
    if len(sys.argv) < 2:
        print("Usage: python photo_capture.py <save_path>")
        return
    save_path = sys.argv[1]
    save_dir = os.path.dirname(save_path)
    os.makedirs(save_dir, exist_ok=True)
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Unable to open camera.")
        return
    print("Press SPACE to capture photo, ESC to exit.")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break
        cv2.imshow('Capture Photo', frame)
        key = cv2.waitKey(1)
        if key % 256 == 27:  # ESC
            print("Escape hit, closing...")
            break
        elif key % 256 == 32:  # SPACE
            cv2.imwrite(save_path, frame)
            print(f"Photo saved to {save_path}")
            break
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
