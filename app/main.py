from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
import valkey.asyncio as valkey

from app import Settings, __version__, get_settings


class ItemPayload(BaseModel):
    value: str = Field(..., min_length=1, max_length=4096)
    ttl_seconds: int | None = Field(default=None, ge=1, le=86400)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    client = valkey.Valkey(
        host=settings.valkey_host,
        port=settings.valkey_port,
        db=settings.valkey_db,
        password=settings.valkey_password or None,
        decode_responses=True,
    )
    app.state.valkey = client
    try:
        await client.ping()
        yield
    finally:
        await client.aclose()


def get_valkey(request: Request) -> valkey.Valkey:
    client: valkey.Valkey | None = getattr(request.app.state, "valkey", None)
    if client is None:
        raise HTTPException(status_code=503, detail="Valkey client is not initialized")
    return client


settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    version=__version__,
    lifespan=lifespan,
)


@app.get("/health")
async def health_check(client: valkey.Valkey = Depends(get_valkey)) -> dict[str, str]:
    pong = await client.ping()
    return {
        "status": "ok" if pong else "degraded",
        "app": settings.app_name,
        "env": settings.app_env,
        "valkey": "connected" if pong else "unreachable",
    }


@app.post("/visits")
async def increment_visits(client: valkey.Valkey = Depends(get_valkey)) -> dict[str, int]:
    count = await client.incr("app:visits")
    return {"visits": int(count)}


@app.put("/items/{key}")
async def put_item(
    key: str,
    payload: ItemPayload,
    client: valkey.Valkey = Depends(get_valkey),
) -> dict[str, str | int | None]:
    namespaced_key = f"items:{key}"
    await client.set(namespaced_key, payload.value, ex=payload.ttl_seconds)
    return {
        "key": key,
        "value": payload.value,
        "ttl_seconds": payload.ttl_seconds,
    }


@app.get("/items/{key}")
async def get_item(
    key: str,
    client: valkey.Valkey = Depends(get_valkey),
) -> dict[str, str | None]:
    value = await client.get(f"items:{key}")
    if value is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"key": key, "value": value}
