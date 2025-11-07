from fastapi import HTTPException

def http_conflict(detail: str):
    raise HTTPException(status_code=409, detail=detail)