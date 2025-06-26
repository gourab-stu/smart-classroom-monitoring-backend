from pathlib import Path

from loguru import logger


async def cleanup_temp_file(path: str):
    try:
        file_path = Path(path)
        if file_path.exists() and file_path.is_file():
            file_path.unlink()
            logger.debug(f"✅ Deleted temp file: {file_path}")
        else:
            logger.warning(f"⚠️ Temp file not found or is not a file: {file_path}")
    except Exception as e:
        logger.error(f"❌ Failed to delete temp file {path}: {e}")
