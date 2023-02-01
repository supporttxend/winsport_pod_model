from typing import List, Union

from pydantic import BaseModel


class DataSchema(BaseModel):
    data: str = None
    message: Union[str, None] = None


class DetailsSchema(BaseModel):
    status: int
    details: DataSchema
