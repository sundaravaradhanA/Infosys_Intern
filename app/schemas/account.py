from pydantic import BaseModel

class AccountBase(BaseModel):
    bank_name: str
    account_type: str
    balance: float

class AccountCreate(AccountBase):
    user_id: int

class AccountResponse(AccountBase):
    id: int
    user_id: int
    
    class Config:
        from_attributes = True
