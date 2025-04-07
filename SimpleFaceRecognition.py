import os
import cv2
import face_recognition as fr
from pymongo.mongo_client import MongoClient
from dotenv import load_dotenv

load_dotenv("./.env")

uri = os.getenv("MONGODB_URI")

client = MongoClient(uri)
db = client["smart-classroom-monitoring"]
collection = db["face-encodings"]


def capture_face(cap: cv2.VideoCapture, facename: str) -> bool:
    text = ["Press spacebar to capture face", "Capturing face..."]
    color = (0, 255, 0)
    thickness = 2
    keyPressed = 0
    encodingCount = 10
    face_encodings = []
    # processing video feed
    while encodingCount != 0 and True:
        # capturing every frame
        (ret, frame) = cap.read()

        # in case of faulty frame
        if ret is False:
            print("Failed to capture frame")

        # converting from opencv's BGR format to face_recognition's RGB format
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # capturing face_location of the detected faces
        face_locations = fr.face_locations(frame_rgb, model="hog")

        t = text[keyPressed]

        # iterating through all detected faces
        for (top, right, bottom, left) in face_locations:
            # draw rectangle around it
            cv2.rectangle(frame, (left - thickness, top - thickness),
                          (right + thickness, bottom + thickness), color, thickness)
            # put necessary messages on the frame
            cv2.putText(frame, t, (left, top - 10),
                        cv2.FONT_ITALIC, 0.7, color, thickness)
            break

        # lastly, show frame
        cv2.imshow("Video", frame)

        # if ' ' key is pressed, append the consecutive 10 frame encodings with face to list
        if keyPressed == 0 and cv2.waitKey(1) == 32:
            keyPressed = 1
        elif keyPressed == 1:
            fe = fr.face_encodings(frame_rgb)
            if len(fe) > 0:
                face_encoding = fe[0]
                face_encoding_list = face_encoding.tolist()
                face_encodings.append(face_encoding_list)
                encodingCount -= 1

    data = {
        "name": f"{facename}",
        "encoding": face_encodings
    }
    collection.insert_one(data)
    print("face stored in mongodb")
    return True


def detect_faces_live(cap: cv2.VideoCapture) -> None:
    temp = []
    known_face_encodings = []
    known_names = []

    for data in collection.find({}):
        if data:  # Ensure data is found
            known_names.append(data["name"])
            temp.append(data["encoding"])

    known_face_encodings = [
        encoding for row in temp for encoding in row]

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Detect faces
        face_locations = fr.face_locations(frame_rgb)
        face_encodings = fr.face_encodings(frame_rgb, face_locations)

        for face_encoding, (top, right, bottom, left) in zip(face_encodings, face_locations):
            matches = fr.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"

            if True in matches:
                matched_idx = matches.index(True)
                name = known_names[matched_idx] if matched_idx < len(
                    known_names) else "Unknown"  # Get corresponding name

            red = (0, 0, 255)
            green = (0, 255, 0)
            thickness = 2

            # Draw rectangle and text
            cv2.rectangle(frame, (left, top), (right, bottom),
                          red if name == "Unknown" else green, thickness)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX,
                        0.7, red if name == "Unknown" else green, thickness)

        # Show frame
        cv2.imshow("Face Recognition", frame)

        if cv2.waitKey(1) == 27:  # Press 'Esc' to exit
            break
