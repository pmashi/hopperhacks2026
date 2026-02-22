import cv2
import math
from ultralytics import YOLO

# 1. Load the pre-trained YOLOv8 AI model
# (It will automatically download a small 6MB file the first time you run this)
model = YOLO('yolov8n.pt')

# 2. Define our recycling categories based on standard AI object names
RECYCLABLE = ['bottle', 'wine glass', 'cup', 'book']
COMPOSTABLE = ['apple', 'banana', 'orange', 'broccoli', 'carrot', 'pizza', 'donut', 'cake']
# Everything else will default to Non-Recyclable / Trash

# 3. Define colors for our bounding boxes (BGR format for OpenCV)
COLOR_RECYCLABLE = (0, 255, 0)     # Green
COLOR_COMPOSTABLE = (0, 255, 255)  # Yellow
COLOR_TRASH = (0, 0, 255)          # Red

# 4. Start the webcam
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

print("Starting Smart Recycling Bin... Press 'q' to quit.")

while True:
    success, frame = cap.read()
    if not success:
        break

    # 5. Have the AI look at the current frame from the webcam
    results = model(frame, stream=True, verbose=False)

    # 6. Process what the AI found
    for r in results:
        boxes = r.boxes
        for box in boxes:
            # Get the confidence score of the AI (0.0 to 1.0)
            confidence = math.ceil((box.conf[0] * 100)) / 100
            
            # Only show objects the AI is more than 50% sure about
            if confidence > 0.50:
                # Get the name of the object it found
                class_id = int(box.cls[0])
                object_name = model.names[class_id]

                # Determine the category and color
                if object_name in RECYCLABLE:
                    category = "RECYCLABLE"
                    color = COLOR_RECYCLABLE
                elif object_name in COMPOSTABLE:
                    category = "COMPOSTABLE"
                    color = COLOR_COMPOSTABLE
                else:
                    category = "NON-RECYCLABLE"
                    color = COLOR_TRASH

                # Get the coordinates for the bounding box
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                # Draw the box around the object
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)

                # Create the text label (e.g., "RECYCLABLE: bottle 85%")
                label_text = f"{category}: {object_name} {int(confidence*100)}%"

                # Draw the text label above the box
                cv2.putText(frame, label_text, (max(0, x1), max(20, y1 - 10)), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    # 7. Show the live camera feed with our custom AI overlays
    cv2.imshow("Smart Recycling AI", frame)

    # 8. Quit if the 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Clean up the camera when done
cap.release()
cv2.destroyAllWindows()