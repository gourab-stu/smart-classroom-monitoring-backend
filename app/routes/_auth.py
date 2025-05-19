from fastapi import APIRouter, Request

from app.controllers import request_otp, verify_otp
from app.schemas.auth import OTPRequestSchema, OTPVerifySchema


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(path="/request-otp")
async def request_otp_endpoint(req: Request):
    data = await req.json()
    otpReq = OTPRequestSchema(email=data['email'])
    return await request_otp(otpReq)


@router.post(path="/verify-otp")
async def verify_otp_endpoint(req: Request):
    data = await req.json()
    otpVerify = OTPVerifySchema(email=data['email'], otp=data['otp'])
    return await verify_otp(otpVerify)
