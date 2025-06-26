import uuid
from typing import Optional

import cloudinary.uploader
from fastapi import HTTPException, status
from loguru import logger

from app.core.config import get_settings

settings = get_settings()


async def upload_to_cloudinary(
    file_content: bytes, folder: str = "assignments", public_id: Optional[str] = None
) -> str:
    try:
        if len(file_content) > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size exceeds 10MB limit",
            )

        if not public_id:
            public_id = f"{uuid.uuid4().hex}"

        result = cloudinary.uploader.upload(
            file_content,
            public_id=public_id,
            resource_type="auto",
            folder=f"{settings.CLOUDINARY_FOLDER}/{folder}",
            overwrite=False,
        )

        return result["secure_url"]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Upload failed")
