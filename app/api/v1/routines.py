# ├── routines/
# │   ├── GET /

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_paper_by_paper_code_endpoint_dependency
from app.api.exceptions import server_error_exception
from app.core.sqlalchemy import get_postgres_session
from app.database.models.postgresql import Routine
from app.schemas.api_response import MessageResponse
from app.schemas.routine import RoutineInDB

router = APIRouter(prefix="/routines", tags=["Routines"])


@router.get("/", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def get_routine_endpoint(
    data: Annotated[dict, Depends(get_paper_by_paper_code_endpoint_dependency)],
    db: Annotated[AsyncSession, Depends(get_postgres_session)],
):
    try:
        stmt = select(Routine)
        result = await db.execute(stmt)
        routine = result.scalars().all()

        # if not paper:
        #     raise paper_not_found_exception

        return MessageResponse(
            content=[RoutineInDB.model_validate(r) for r in routine],
            message="Routine fetched successfully",
            success=True,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(e)
        logger.error(e.__class__)
        raise server_error_exception
