from fastapi import APIRouter

from app.schemas.auth import OTPRequestSchema, OTPVerifySchema


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/request-otp")
async def request_otp(data: OTPRequestSchema):
    pass


@router.post("/verify-otp")
async def verify_otp(data: OTPVerifySchema):
    pass


# @router.post(path="/request-otp")
# async def request_otp(req: Request):
#     incoming_data = await req.json()
#     email: str = incoming_data['email']
#     if await Student.find({'email': email}).count() == 1 or await Teacher.find({'email': email}).count() == 1:
#         otp: int = randint(a=123456, b=987456)
#         subject = 'OTP Verification'
#         body: str = f'Your OTP to Sign In to Smart classroom is {otp}. Don\'t share it with anyone.'
#         document = {'user': email, 'timestamp': datetime.now(), 'otp': otp}
#         await OTP.insert_one(document=document)
#         send_email(receiver_email=email, subject=subject, body=body)
#     else:
#         return Response(content=ResponseModel(status=False, message='User not found'), status_code=404)


# @router.post(path="/verify-otp")
# async def verify_otp(req: Request):
#     pass
