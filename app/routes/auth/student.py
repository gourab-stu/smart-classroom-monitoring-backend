from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/student", tags=["Auth - Student"])


@router.post("/register")
async def register_student():
    pass


@router.post("/login")
async def login_student(file: UploadFile = File(...)):
    # Simulate processing time (e.g., face recognition)

    # You can even print file.filename if you want
    print(f"Received file: {file.filename}")

    # Respond with dummy login success
    return JSONResponse(content={
        "login": True,
        "studentId": "0123456789abcdef"
    })
