import datetime
from pydantic import BaseModel, EmailStr


class SignUpIn(BaseModel):
    fullname: str
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    fullname: str
    email: EmailStr
    created_at: datetime.datetime

    class Config:
        from_attributes = True
