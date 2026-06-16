import uuid
from fastapi import File, UploadFile
from pydantic import BaseModel

class PipelineRequest(BaseModel):
    file: UploadFile = File(...) # (.xlsx, .xls)
    client_id: str
    sheet_name: str # (Optional, default: primera hoja) 

class PipelineResponse(BaseModel):
    process_id: uuid
    status: str
    message: str