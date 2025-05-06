from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
from ...db.face_recognition import crud
from ...modules import email, face_recognition_utils as fru

router = APIRouter(prefix="/student", tags=["Auth - Student"])


@router.post("/register")
async def register_student():
    pass


@router.post("/login")
async def login_student(file: UploadFile = File(...)):
    # You can even print file.filename if you want
    print(f"Received file: {file.filename}")

    print(file.content_type)
    bytes = await file.read()
    frame = fru.to_frame(data=bytes)
    known_faces = crud.load_known_faces()
    result = fru.detect_face_info(frame, known_faces)
    print(result)

    # Send email to client
    email.send_email(result['email'], "testing", "purpose")
    print("✅ Email sent successfully.")

    # Respond with dummy login success
    return JSONResponse(content={
        "login": True,
        "studentId": result['id']
    })
