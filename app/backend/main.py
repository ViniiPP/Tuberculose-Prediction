from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from pydantic import BaseModel, Field
from typing import Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pipeline.pipeline_final import predict

app = FastAPI(title="LTFU API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)


class PacienteInput(BaseModel):
    idade_anos: int = Field(..., ge=18, le=120)
    CS_SEXO: Optional[str] = None
    CS_RACA: Optional[str] = None
    CS_ESCOL_N: Optional[str] = None
    NU_CONTATO: Optional[int] = 0
    TRATAMENTO: Optional[str] = None
    HIV: Optional[str] = None
    BACILOSC_E: Optional[str] = None
    RAIOX_TORA: Optional[str] = None
    SG_UF_NOT: Optional[str] = None
    AGRAVAIDS: Optional[str] = None
    AGRAVALCOO: Optional[str] = None
    AGRAVDIABE: Optional[str] = None
    AGRAVDOENC: Optional[str] = None
    AGRAVDROGA: Optional[str] = None
    AGRAVTABAC: Optional[str] = None
    POP_LIBER: Optional[str] = None
    POP_RUA: Optional[str] = None
    TRAT_SUPER: Optional[str] = None
    INSTITUCIO: Optional[str] = None
    BENEF_GOV: Optional[str] = None


@app.get("/api/health")
def health():
    return {"status": "ok", "servico": "LTFU API"}


@app.post("/predict")
def predicao(dados: PacienteInput):
    try:
        resultado = predict(dados.model_dump())
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Servir o frontend estaticamente (as rotas de API têm prioridade)
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
if os.path.isdir(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")