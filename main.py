import os
from fastapi import FastAPI
from contextlib import asynccontextmanager
import db
from routers import auth, expense
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv

load_dotenv()

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8000"
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.create_db_and_tables()  # Ensure async
    yield
    print('Gracefully shutting down')
    await db.engine.dispose()  # Ensure async disposal

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Authorization"],
)

app.include_router(auth.auth_router)
app.include_router(expense.expense_router)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
