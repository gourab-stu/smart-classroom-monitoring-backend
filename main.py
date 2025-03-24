import cv2
import SimpleFaceRecognition as sfr

# using webcam
cap = cv2.VideoCapture(0)

# capture_face(cap, "faces/temp.jpg")
sfr.detect_faces_live(cap, "faces")

cap.release()
cv2.destroyAllWindows()
