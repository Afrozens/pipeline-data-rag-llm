from fastapi import Header, HTTPException, Depends
from app.core.config import settings


def verify_api_key(x_api_key: str = Header(None)):
    if x_api_key != settings.SECRET_KEY:
        raise HTTPException(status_code=403, detail="Invalid or missing API Key")
    return x_api_key
