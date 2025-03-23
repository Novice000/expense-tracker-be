from pydantic import BaseModel
from typing import Optional

class UserIn(BaseModel):
    username: str
    password: str
    budget: float

class ExpenseIn(BaseModel):
    amount: float
    description: str
    
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str
    
class ReturnMessage(BaseModel):
    success: bool
    message: str
    payload: Optional[dict]