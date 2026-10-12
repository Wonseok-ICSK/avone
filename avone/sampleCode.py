import cv2

# Replace with your device number, e.g., 0 for /dev/video0, 1 for /dev/video1
device_index = 0
cap = cv2.VideoCapture(device_index)

# Check if the capture card is opened successfully
if not cap.isOpened():
    print("Error: Could not open video device.")
    exit()

# Set frame width and height if needed
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    if not ret:
        print("Failed to grab frame")
        break

    # Display the resulting frame
    cv2.imshow('Capture Card Output', frame)

    # Break the loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture and close windows
cap.release()
cv2.destroyAllWindows()