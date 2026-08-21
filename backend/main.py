"""Application entry point: configure FastAPI, CORS, tables, and routers."""

import os

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from backend.database import Base, engine
from backend.routers import analytics, budgets, expenses

load_dotenv()

app = FastAPI(
    title="Expense Tracker & Analytics API",
    version="1.0.0",
    description="REST API powering the Streamlit Expense Tracker frontend.",
)

allowed_origins = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:8501,http://127.0.0.1:8501").split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


@app.on_event("startup")
def create_tables() -> None:
    """Create local tables. Production projects should replace this with migrations."""
    Base.metadata.create_all(bind=engine)


@app.exception_handler(SQLAlchemyError)
async def database_exception_handler(_: Request, __: SQLAlchemyError) -> JSONResponse:
    """Avoid exposing database implementation details to API consumers."""
    return JSONResponse(status_code=500, content={"detail": "A database error occurred. Please try again later."})


@app.get("/", tags=["Health"], summary="Check API availability")
def root() -> dict[str, str]:
    return {"message": "Expense Tracker API is running", "docs": "/docs"}


@app.get("/health", tags=["Health"], summary="Health-check endpoint")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(expenses.router)
app.include_router(analytics.router)
app.include_router(budgets.router)
