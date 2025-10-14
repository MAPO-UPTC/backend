import uuid
from typing import Optional
from pydantic import BaseModel


class UserEntities(BaseModel):
    id: uuid.UUID
    first_name: str
    last_name: str
    role: str
    second_first_name: Optional[str] = None
    second_last_name: Optional[str] = None
    phone_number: Optional[str] = None
    phone_code: Optional[str] = None

    class Config:
        orm_mode = True
