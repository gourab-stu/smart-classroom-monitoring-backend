from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.redis import get_redis
from app.core.sqlalchemy import get_db_session
from app.database.models.postgresql import Student, Teacher
from app.database.models.redis import OTP
from app.routes.auth import admin
from app.schemas.auth import OTPRequestSchema, OTPVerifySchema, StudentInfoSchema
from app.services.email import send_email
from app.utilities.otp import generate_otp


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(path="/get-student-info")
async def get_student_info_endpoint(
    studentInfo: StudentInfoSchema, db: AsyncSession = Depends(get_db_session)
):
    try:
        print("/auth/get-student-info -> ", end="")
        # find student
        result = await db.execute(
            select(Student).where(Student.reg_no == studentInfo.reg_no)
        )
        student = result.scalars().first()

        # close database connection
        await db.close()

        # if student not found -> send "not found" response
        if not result:
            return JSONResponse(
                content={"success": False, "message": "No student found"},
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # send success response with the student data
        return JSONResponse(
            content={
                "success": True,
                "message": "Student found",
                "data": student,
            },
            status_code=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        # if any errors -> print to console
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong",
        )


@router.post(path="/request-otp")
async def request_otp_endpoint(
    otpReq: OTPRequestSchema, db: AsyncSession = Depends(get_db_session)
):
    try:
        print("/auth/request-otp -> ", end="")
        # find student
        result = await db.execute(select(Student).where(Student.email == otpReq.email))
        student = result.scalars().first()

        # if student is not found -> find teacher
        if not student:
            next_result = await db.execute(
                select(Teacher).where(Teacher.email == otpReq.email)
            )
            teacher = next_result.scalars().first()
            # if teacher is also not found -> return "user not found" response
            if not teacher:
                return JSONResponse(
                    content={"success": False, "message": "User not found"},
                    status_code=status.HTTP_404_NOT_FOUND,
                )

        # generate otp for user
        otp: OTP = await generate_otp(profile_id=otpReq.email)

        # store otp in redis
        redis = await get_redis()
        await redis.setex(
            name=otp.key, time=settings.OTP_EXPIRY_SECONDS, value=otp.value
        )

        # send verification email to user
        subject: str = "OTP verification for MLeC"
        body: str = f"Your OTP to sign in to MLeC is {otp.value}"
        await send_email(to_email=otpReq.email, subject=subject, content=body)

        # close database connection
        await db.close()

        # return success response
        return JSONResponse(
            content={"success": True, "message": "OTP sent successfully"},
            status_code=status.HTTP_200_OK,
        )
    except Exception as e:
        # if any errors -> print to console
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong",
        )


@router.post(path="/verify-otp")
async def verify_otp_endpoint(
    otpVerify: OTPVerifySchema, db: AsyncSession = Depends(get_db_session)
):
    try:
        print("/auth/verify-otp -> ", end="")
        # send authorization tokens and successful response
        # find the value with the key in redis
        redis = await get_redis()
        key = OTP.get_key(is_profile_id=True, profile_id=otpVerify.email)
        stored_otp = await redis.get(key)

        # if no value found -> send "invalid otp" response
        if not stored_otp or str(object=stored_otp) != str(object=otpVerify.otp):
            subject: str = "Unsuccessful Sign In Attempt"
            body: str = f"Your sign in attempt on {datetime.now().strftime('%A, %d %B %Y')} at {datetime.now().strftime('%I:%M %p')} was unsuccessful"
            await send_email(to_email=otpVerify.email, subject=subject, content=body)
            return False

        # delete redis key-value pair
        await redis.delete(key)

        # send "sign in successful" email
        subject: str = "Sign In Successful"
        body: str = f"Your sign in attempt on {datetime.now().strftime('%A, %d %B %Y')} at {datetime.now().strftime('%I:%M %p')} was successful"
        await send_email(to_email=otpVerify.email, subject=subject, content=body)
        return True
        await db.close()

        if not result:
            return JSONResponse(
                content={"success": False, "message": "Invalid OTP"},
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        return JSONResponse(
            content={"success": True, "message": "OTP verification successful"},
            status_code=status.HTTP_200_OK,
        )
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong",
        )


router.include_router(admin.router)
