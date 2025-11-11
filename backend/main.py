import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import List

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import Column, DateTime, Integer, String, Text, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/app.db")
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "*")
if allowed_origins_env.strip() == "*":
    ALLOWED_ORIGINS = ["*"]
else:
    ALLOWED_ORIGINS = [origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()]

def _sqlite_connect_args(url: str) -> dict:
    return {"check_same_thread": False} if url.startswith("sqlite") else {}


def _ensure_data_dir(url: str) -> None:
    if url.startswith("sqlite"):
        db_path = url.split("///")[-1]
        data_dir = Path(db_path).parent
        data_dir.mkdir(parents=True, exist_ok=True)


_ensure_data_dir(DATABASE_URL)
engine = create_engine(DATABASE_URL, connect_args=_sqlite_connect_args(DATABASE_URL))
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()


class Budget(Base):
    __tablename__ = "budgets"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    timestamp = Column(Integer, nullable=False)
    state = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)


Base.metadata.create_all(bind=engine)


class BudgetPayload(BaseModel):
    name: str
    timestamp: int
    state: dict


class BudgetResponse(BudgetPayload):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class BudgetListResponse(BaseModel):
    id: str
    name: str
    timestamp: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI(title="Presupuestos Interactivo API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

ROOT_PATH = Path(__file__).resolve().parents[1]
HTML_FILE = ROOT_PATH / "presupuesto.html"


@app.get("/", response_class=FileResponse)
def index() -> FileResponse:
    if not HTML_FILE.exists():
        raise HTTPException(status_code=404, detail="Archivo principal no encontrado")
    return FileResponse(HTML_FILE)


@app.get("/api/health")
def healthcheck():
    return {"status": "ok"}


@app.get("/api/budgets", response_model=List[BudgetListResponse])
def list_budgets(db: Session = Depends(get_db)):
    budgets = db.query(Budget).order_by(Budget.timestamp.desc()).all()
    return budgets


@app.post("/api/budgets", response_model=BudgetResponse, status_code=201)
def create_budget(payload: BudgetPayload, db: Session = Depends(get_db)):
    budget = Budget(
        id=str(uuid.uuid4()),
        name=payload.name,
        timestamp=payload.timestamp,
        state=json.dumps(payload.state),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(budget)
    db.commit()
    db.refresh(budget)
    return BudgetResponse(
        id=budget.id,
        name=budget.name,
        timestamp=budget.timestamp,
        state=payload.state,
        created_at=budget.created_at,
        updated_at=budget.updated_at,
    )


@app.get("/api/budgets/{budget_id}", response_model=BudgetResponse)
def read_budget(budget_id: str, db: Session = Depends(get_db)):
    budget = db.query(Budget).filter(Budget.id == budget_id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Presupuesto no encontrado")
    return BudgetResponse(
        id=budget.id,
        name=budget.name,
        timestamp=budget.timestamp,
        state=json.loads(budget.state),
        created_at=budget.created_at,
        updated_at=budget.updated_at,
    )


@app.put("/api/budgets/{budget_id}", response_model=BudgetResponse)
def update_budget(budget_id: str, payload: BudgetPayload, db: Session = Depends(get_db)):
    budget = db.query(Budget).filter(Budget.id == budget_id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Presupuesto no encontrado")

    budget.name = payload.name
    budget.timestamp = payload.timestamp
    budget.state = json.dumps(payload.state)
    budget.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(budget)
    return BudgetResponse(
        id=budget.id,
        name=budget.name,
        timestamp=budget.timestamp,
        state=json.loads(budget.state),
        created_at=budget.created_at,
        updated_at=budget.updated_at,
    )


@app.delete("/api/budgets/{budget_id}", status_code=204)
def delete_budget(budget_id: str, db: Session = Depends(get_db)):
    budget = db.query(Budget).filter(Budget.id == budget_id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Presupuesto no encontrado")

    db.delete(budget)
    db.commit()
