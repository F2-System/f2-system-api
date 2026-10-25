
import os
import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI(title="F2 SYSTEM API Proxy")

BOT_API = os.getenv(
    "BOT_API_URL",
    "http://th-bkk03.altare.global:25163"
).rstrip("/")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://f2-system.github.io"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)

@app.get("/")
@app.get("/health")
async def health():
    return {"ok": True, "service": "F2 SYSTEM API Proxy"}

@app.post("/pedido")
async def pedido(request: Request):
    try:
        body = await request.json()

        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                f"{BOT_API}/pedido",
                json=body,
            )

        try:
            result = response.json()
        except ValueError:
            result = {"detail": "Resposta inválida da API do bot"}

        return JSONResponse(
            content=result,
            status_code=response.status_code,
        )

    except httpx.RequestError:
        raise HTTPException(
            status_code=502,
            detail="Não foi possível conectar à API do bot na Altare."
        )
