from fastapi import (
    HTTPException,
    Depends,
    APIRouter,
    status,
    HTTPException,
    Security,
    BackgroundTasks,
)
from sqlalchemy.orm import Session
from db.session import get_db


router = APIRouter()


@router.get("/")
def train():

    return {"status": status.HTTP_200_OK, "data": max_index, "feature": feature}