from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True)
    password: str
    budget: float
    expense: list["Expense"] = Relationship(back_populates="user")  # ✅ Fixed List type

class Expense(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    user: Optional["User"] = Relationship(back_populates="expense")
    amount: float
    description: str
    timestamp: datetime = Field(default_factory=datetime.now)
