from fastapi import FastAPI
from contextlib import asynccontextmanager
import db
from routers import auth, expense
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8000",
    "*"
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    db.create_db_and_tables()
    yield
    print('gracefully shutting down')
    db.engine.dispose()
    
app = FastAPI(lifespan=lifespan)
    
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.auth_router)
app.include_router(expense.expense_router)

