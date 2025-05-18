from fastapi import APIRouter, Request

from app.schemas.auth import OTPRequestSchema, OTPVerifySchema


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(path="/request-otp")
async def request_otp_endpoint(req: Request):
    pass


@router.post("/verify-otp")
async def verify_otp(data: OTPVerifySchema):
    pass
