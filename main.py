import cv2
import SimpleFaceRecognition as SFR

# using webcam
cap = cv2.VideoCapture(0)

# SFR.capture_face(cap, "gourab.jpg")
SFR.detect_faces_live(cap)

cap.release()
cv2.destroyAllWindows()
