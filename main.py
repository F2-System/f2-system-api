
import os
import httpx
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException
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

class PedidoCalculadora(BaseModel):
    ticket: str = Field(min_length=20, max_length=200)
    current_rank: str
    desired_rank: str
    reward: bool
    upador: str
    price: str

@app.get("/")
@app.get("/health")
async def health():
    return {"ok": True, "service": "F2 SYSTEM API Proxy"}

@app.post("/pedido")
async def pedido(body: PedidoCalculadora):
    try:
        dados = body.model_dump()

        preco = (
            dados["price"]
            .replace("R$", "")
            .replace(" ", "")
            .replace(".", "")
            .replace(",", ".")
        )
        dados["price"] = float(preco)

        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                f"{BOT_API}/pedido",
                json=dados,
            )

        try:
            result = response.json()
        except ValueError:
            result = {"detail": "Resposta inválida da API do bot"}

        return JSONResponse(
            content=result,
            status_code=response.status_code,
        )

    except ValueError:
        raise HTTPException(
            status_code=422,
            detail="O preço enviado é inválido."
        )
    except httpx.RequestError:
        raise HTTPException(
            status_code=502,
            detail="Não foi possível conectar à API do bot na Altare."
        )
