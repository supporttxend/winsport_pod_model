from pydantic import BaseModel
from typing import List, Union

class DataSchema(BaseModel):
    data: str = None
    message: Union[str, None] = None

class DetailsSchema(BaseModel):
    status: int
    details: DataSchema
