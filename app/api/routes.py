"""Rotas da API para análise de notas fiscais."""

from fastapi import APIRouter, HTTPException
from schemas.invoice import InvoiceAnalysisRequest, InvoiceAnalysisResponse
from ai.analyzer import analyze_invoice

router = APIRouter()


@router.post("/analyze", response_model=InvoiceAnalysisResponse)
async def analyze_invoice_route(request: InvoiceAnalysisRequest):
    """Analisa uma nota fiscal utilizando IA local (Ollama).

    Recebe o texto bruto da nota fiscal (XML, texto OCR, ou conteúdo colado)
    e retorna:
    - Relatório tributário detalhado em linguagem natural
    - Dados estruturados extraídos
    - Valores por extenso em português
    """
    try:
        result = analyze_invoice(request.text)

        return InvoiceAnalysisResponse(
            report=result["report"],
            structured_data=result["structured_data"],
            valor_total_extenso=result.get("valor_total_extenso", ""),
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao analisar nota fiscal: {str(e)}",
        )
