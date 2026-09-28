"""NF Analyzer AI - API Backend.

Sistema de análise inteligente de Notas Fiscais brasileiras (NF-e/NFS-e)
utilizando IA local via Ollama (LLaMA 3 / Mistral).

Funcionalidades:
- Extração de dados de NF-e XML
- Conversão de valores por extenso em PT-BR
- Identificação de impostos (ICMS, ISS, IPI, PIS, COFINS)
- Relatório tributário em linguagem natural
- 100% offline e privado
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router as analyze_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

app = FastAPI(
    title="NF Analyzer AI",
    description=(
        "API de análise inteligente de Notas Fiscais brasileiras. "
        "Utiliza IA local (Ollama) para extrair dados, escrever valores "
        "por extenso e identificar impostos a pagar."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze_router, prefix="/api", tags=["Análise Fiscal"])


@app.get("/")
def health_check():
    """Verificação de saúde da API."""
    return {
        "status": "ok",
        "service": "NF Analyzer AI",
        "backend": "Ollama (modelo local)",
    }
