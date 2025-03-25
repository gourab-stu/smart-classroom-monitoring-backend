import cv2
import SimpleFaceRecognition as SFR

# using webcam
cap = cv2.VideoCapture(0)

# SFR.capture_face(cap, "faces/uma.jpg")
SFR.detect_faces_live(cap, "faces")

cap.release()
cv2.destroyAllWindows()
