import uuid
from typing import Dict, List, Optional
from fastapi import File, UploadFile
from pydantic import BaseModel, Field


class PipelineRequest(BaseModel):
    file: UploadFile = File(...)
    client_id: str
    sheet_name: str = ""


class PipelineResponse(BaseModel):
    process_id: uuid.UUID
    status: str
    message: str


class DetectedFormat(BaseModel):
    format_name: str = Field(
        description="Descriptive name of the detected format"
    )
    detected_columns: Dict[str, str] = Field(
        description="Map of {excel_column: semantic_description}"
    )
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Confidence level in detection (0.0 - 1.0)"
    )
    contains_travelers: bool = Field(
        description="Whether the data includes a travelers column"
    )


class FieldMapping(BaseModel):
    mapping: Dict[str, Optional[str]] = Field(
        description="""Map of {excel_column_name: unified_schema_path}.
        Use dot notation for nested fields, e.g.:
        - 'nombre_completo' -> 'passenger.first_name'
        - 'fecha_viaje' -> 'trip.start_date'
        - 'precio' -> 'amount'
        - unmapped columns: null
        Target must be a valid path within TripRecord."""
    )
    unmapped_columns: List[str] = Field(
        description="Columns that could not be mapped to the schema"
    )
    notes: Optional[str] = Field(
        default=None,
        description="Additional notes about the mapping"
    )