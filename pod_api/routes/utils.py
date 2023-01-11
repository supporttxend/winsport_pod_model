from fastapi import HTTPException
from schemas import DetailsSchema


def exception_callback(status_code, detail=None, headers=None):
    raise HTTPException(status_code=status_code, detail=detail, headers=headers)