import os
from typing import Annotated
from sqlmodel import SQLModel, Session, create_engine
from fastapi import Depends
from dotenv import load_dotenv
load_dotenv()

database_path = os.getenv("DATABASE_URL")
connection_args = {
    "check_same_thread": False
}
engine = create_engine(database_path, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    
def get_session():
    with Session(engine) as session:
        yield session
        
session_dependency = Annotated[Session, Depends(get_session)]