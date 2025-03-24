import cv2
import face_recognition as fr
from pathlib import Path


def capture_face(cap: cv2.VideoCapture, filename: str) -> bool:
    text = "Press 'Esc' key to capture face"
    color = (0, 255, 0)
    thickness = 2
    # processing video feed
    while True:
        # capturing every frame
        (ret, frame) = cap.read()

        # in case of faulty frame
        if ret == False:
            print("Failed to capture frame")

        # converting from opencv's BGR format to face_recognition's RGB format
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # capturing face_location of the detected faces
        face_locations = fr.face_locations(frame_rgb, model="hog")

        # iterating through the 1st detected face among all detected faces
        for (top, right, bottom, left) in face_locations:
            # draw rectangle around it
            cv2.rectangle(frame, (left - thickness, top - thickness),
                          (right + thickness, bottom + thickness), color, thickness)
            # put necessary messages on the frame
            cv2.putText(frame, text, (left, top - 10),
                        cv2.FONT_ITALIC, 0.7, color, thickness)
            face = cv2.cvtColor(
                frame[top: bottom, left: right], cv2.COLOR_BGR2GRAY)
            break

        # lastly, show frame
        cv2.imshow("Video", frame)

        # if 'Esc' key is pressed, write the frame to disk and stop
        if cv2.waitKey(1) == 27:
            cv2.imwrite(f"{filename}", face)
            break

    return True


def detect_faces_live(cap: cv2.VideoCapture, folder_name_with_known_faces: str) -> None:
    # Load known face encodings
    # List all images in folder
    paths = list(Path(f"{folder_name_with_known_faces}").glob("*"))
    known_face_encodings = []

    for img_path in paths:
        img = cv2.imread(str(img_path))
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodings = fr.face_encodings(img_rgb)

        if encodings:  # Ensure encodings are found
            known_face_encodings.append(encodings[0])

    # Extract file names (without extension)
    known_names = [path.stem for path in paths]

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
                name = known_names[matched_idx]  # Get corresponding name

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
