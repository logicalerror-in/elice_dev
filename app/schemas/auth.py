from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

class SignUpPayload(BaseModel):
    fullname: str = Field(min_length=1, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)  # bcrypt 72B limit

class SignUpResponse(BaseModel):
    id: int
    fullname: str
    email: EmailStr
    created_at: datetime

class UserOut(BaseModel):
    id: int
    fullname: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True