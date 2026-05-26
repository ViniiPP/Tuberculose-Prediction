from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
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
    idade_anos: Optional[int] = None
    CS_SEXO: Optional[str] = None
    CS_RACA: Optional[str] = None
    CS_ESCOL_N: Optional[str] = None
    NU_CONTATO: Optional[int] = 0
    TRATAMENTO: Optional[str] = None
    HIV: Optional[str] = None
    BACILOSC_E: Optional[str] = None
    RAIOX_TORA: Optional[str] = None
    SG_UF_NOT: Optional[str] = None
    AGRAVAIDS: Optional[str] = "9"
    AGRAVALCOO: Optional[str] = "9"
    AGRAVDIABE: Optional[str] = "9"
    AGRAVDOENC: Optional[str] = "9"
    AGRAVDROGA: Optional[str] = "9"
    AGRAVTABAC: Optional[str] = "9"
    POP_LIBER: Optional[str] = "2"
    POP_RUA: Optional[str] = "2"
    TRAT_SUPER: Optional[str] = "9"
    INSTITUCIO: Optional[str] = "0"
    BENEF_GOV: Optional[str] = "9"


@app.get("/")
def health():
    return {"status": "ok", "servico": "LTFU API"}


@app.post("/predict")
def predicao(dados: PacienteInput):
    try:
        resultado = predict(dados.model_dump())
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
