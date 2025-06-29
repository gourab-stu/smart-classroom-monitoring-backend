from pathlib import Path

from loguru import logger


async def delete_file(path: str):
    try:
        file_path = Path(path)
        if file_path.exists() and file_path.is_file():
            file_path.unlink()
            logger.debug(f"✅ Deleted file: {file_path}")
        else:
            logger.warning(f"⚠️ File not found or is not a file: {file_path}")
    except Exception as e:
        logger.error(f"❌ Failed to delete file {path}: {e}")
