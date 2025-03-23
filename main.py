from fastapi import FastAPI
from contextlib import asynccontextmanager
import db
from routers import auth, expense


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.create_db_and_tables()
    yield
    print('gracefully shutting down')
    db.engine.dispose()
    
app = FastAPI(lifespan=lifespan)
    
app.include_router(auth.auth_router)
app.include_router(expense.expense_router)

