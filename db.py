from typing import Annotated
from sqlmodel import SQLModel, Session, create_engine
from fastapi import Depends


database_path = 'sqlite:///database.db'
connection_args = {
    "check_same_thread": False
}
engine = create_engine(database_path, connect_args=connection_args, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    
def get_session():
    with Session(engine) as session:
        yield session
        
session_dependency = Annotated[Session, Depends(get_session)]