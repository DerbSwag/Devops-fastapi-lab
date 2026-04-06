import os
import logging
import json
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, Response, Depends
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import text, String, DateTime, func


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
        }
        if record.exc_info and record.exc_info[0]:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry)


handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
log_level = os.getenv("LOG_LEVEL", "info").upper()
logging.basicConfig(level=getattr(logging, log_level, logging.INFO), handlers=[handler])
logger = logging.getLogger("fastapi-app")

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "appdb")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_async_engine(DATABASE_URL, pool_size=5, max_overflow=5)
async_session = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class Item(Base):
    __tablename__ = "items"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up — connecting to database")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables ready")
    except Exception:
        logger.error("Failed to connect to database", exc_info=True)
    yield
    logger.info("Shutting down — disposing database engine")
    await engine.dispose()


app = FastAPI(lifespan=lifespan)


async def get_db():
    async with async_session() as session:
        yield session


@app.get("/")
def read_root():
    return {
        "message": "DevOps Lab v3 - GitOps with ArgoCD!",
        "env": os.getenv("APP_ENV", "not set"),
        "version": os.getenv("APP_VERSION", "not set"),
        "log_level": os.getenv("LOG_LEVEL", "not set"),
    }


@app.get("/healthz")
def liveness():
    return {"status": "alive"}


@app.get("/readyz")
async def readiness(response: Response):
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception:
        logger.warning("Readiness check failed — DB unreachable", exc_info=True)
        response.status_code = 503
        return {"status": "not ready", "reason": "database unreachable"}


@app.get("/secret-check")
def secret_check():
    api_key = os.getenv("API_KEY", "not set")
    return {"api_key_exists": api_key != "not set", "api_key_length": len(api_key)}


@app.post("/items", status_code=201)
async def create_item(name: str, db: AsyncSession = Depends(get_db)):
    item = Item(name=name)
    db.add(item)
    await db.commit()
    await db.refresh(item)
    logger.info("Item created", extra={"item_id": item.id, "name": item.name})
    return {"id": item.id, "name": item.name, "created_at": item.created_at.isoformat()}


@app.get("/items")
async def list_items(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT id, name, created_at FROM items ORDER BY id"))
    return [{"id": r.id, "name": r.name, "created_at": r.created_at.isoformat()} for r in result]
