from pydantic import BaseModel

class UserBase(BaseModel):
    name: str
    email: str
    phone: str
    kyc_status: str = "Pending"

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    
    class Config:
        from_attributes = True
