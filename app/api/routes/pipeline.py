from typing import Any
from fastapi import APIRouter, Depends
from pymongo.database import Database

from app.schemas.pipeline import PipelineRequest, PipelineResponse
from app.api.deps import verify_api_key
from app.core.db import get_db

router = APIRouter(
    prefix="/pipeline",
    tags=["pipeline"],
    dependencies=[Depends(verify_api_key)],
)


@router.post("/upload", response_model=PipelineResponse)
def create_item(
    *, db: Database = Depends(get_db), body: PipelineRequest
) -> Any:
    """
    Create new pipeline.
    """
    return PipelineResponse(
        process_id=...,
        status="pending",
        message="Pipeline created",
    )
