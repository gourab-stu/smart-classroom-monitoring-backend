from fastapi import HTTPException, status

server_error_exception = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail="Internal Server Error",
)

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
)

logout_exception = HTTPException(
    status_code=status.HTTP_409_CONFLICT, detail="Please Logout first"
)

usr_not_found_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="User not found, try again or contact admin for more details",
)

email_empty_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST, detail="Email cannot be empty"
)

revoke_token_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Token has been revoked",
)

refresh_token_not_found_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token not found"
)

authorization_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="You are not authorized to access or modify this resource",
)

assignment_integrity_exception = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="There is another assignment with the same title",
)

otp_sending_failed_exception = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail="Failed to send OTP",
)

multiple_otp_request_exception = HTTPException(
    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
    detail="Please wait before requesting another OTP",
)

otp_expired_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="OTP expired, please request a new one",
)

invalid_otp_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid OTP, please try again",
)

auth_failure_exception = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail="Authentication failed",
)

logout_failure_exception = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Logout failed"
)

invalid_refresh_token_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
)

token_refreshing_failure = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail="Token refresh failed",
)

assignment_not_found_exception = HTTPException(
    status_code=404, detail="Assignment not found"
)

filetype_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST, detail="File type not supported"
)

file_size_exceeds_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST, detail="File size exceeds 10MB limit"
)

attachment_not_found_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="Attachment not found"
)

no_submissions_found_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="No submission found for the assignment",
)

user_email_integrity_exception = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Email already exists",
)

user_mobile_no_integrity_exception = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Mobile no already exists",
)

invalid_role_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role selected"
)

elective_papers_missing_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST, detail="Elective papers cannot be empty"
)


__all__ = [
    "server_error_exception",
    "credentials_exception",
    "logout_exception",
    "usr_not_found_exception",
    "email_empty_exception",
    "revoke_token_exception",
    "refresh_token_not_found_exception",
    "authorization_exception",
    "assignment_integrity_exception",
    "otp_sending_failed_exception",
    "multiple_otp_request_exception",
    "otp_expired_exception",
    "invalid_otp_exception",
    "auth_failure_exception",
    "logout_failure_exception",
    "invalid_refresh_token_exception",
    "token_refreshing_failure",
    "assignment_not_found_exception",
    "filetype_exception",
    "file_size_exceeds_exception",
    "attachment_not_found_exception",
    "no_submissions_found_exception",
    "user_email_integrity_exception",
    "user_mobile_no_integrity_exception",
    "invalid_role_exception",
    "elective_papers_missing_exception",
]
