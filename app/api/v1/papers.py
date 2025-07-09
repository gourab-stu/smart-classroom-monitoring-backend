# ├── papers/
# │   ├── GET /
# │   ├── POST /
# │   ├── GET /{paper_code}
# │   ├── PUT /{paper_code}
# │   ├── DELETE /{paper_code}
# │   └── GET /{paper_code}/students

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_paper_by_paper_code_endpoint_dependency
from app.api.exceptions import paper_not_found_exception, server_error_exception
from app.core.sqlalchemy import get_postgres_session
from app.database.models.postgresql import Paper
from app.schemas.api_response import MessageResponse
from app.schemas.paper import PaperResponse

router = APIRouter(prefix="/papers", tags=["Papers"])


@router.get("/")
def get_papers_endpoint():
    pass


@router.post("/")
def get_papers_post_endpoint():
    pass


@router.get(
    "/{paper_code}", response_model=MessageResponse, status_code=status.HTTP_200_OK
)
async def get_paper_by_paper_code_endpoint(
    paper_code: str,
    data: Annotated[dict, Depends(get_paper_by_paper_code_endpoint_dependency)],
    db: Annotated[AsyncSession, Depends(get_postgres_session)],
):
    try:
        stmt = select(Paper).where(Paper.paper_code == paper_code)
        result = await db.execute(stmt)
        paper = result.scalar_one_or_none()

        if not paper:
            raise paper_not_found_exception

        return MessageResponse(
            content=PaperResponse.model_validate(paper),
            message="Paper fetched successfully",
            success=True,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(e)
        logger.error(e.__class__)
        raise server_error_exception


@router.put("/{paper_code}")
def put_paper_endpoint():
    pass


@router.delete("/{paper_code}")
def delete_paper_endpoint():
    pass


@router.get("/{paper_code}/students")
def get_paper_students_endpoint():
    pass
