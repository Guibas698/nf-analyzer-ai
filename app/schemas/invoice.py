"""Schemas Pydantic para análise de Notas Fiscais."""

from pydantic import BaseModel, Field
from typing import Optional


class InvoiceAnalysisRequest(BaseModel):
    """Requisição de análise de nota fiscal."""
    text: str = Field(
        ...,
        description="Texto bruto extraído da nota fiscal (XML, texto OCR, ou conteúdo colado)",
        min_length=10,
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "text": "<NFe><infNFe><emit><CNPJ>11222333000181</CNPJ>"
                    "<xNome>TECH SOLUTIONS</xNome></emit>"
                    "<total><ICMSTot><vNF>35692.50</vNF>"
                    "<vICMS>6030.00</vICMS></ICMSTot></total></infNFe></NFe>"
                }
            ]
        }
    }


class TaxDetail(BaseModel):
    """Detalhe de um imposto identificado."""
    nome: str = Field(..., description="Nome do imposto (ex: ICMS, ISS, IPI)")
    valor: float = Field(0.0, description="Valor estimado do imposto em R$")
    valor_extenso: str = Field("", description="Valor por extenso em português")
    aliquota: Optional[str] = Field(None, description="Alíquota aplicada")
    descricao: str = Field("", description="Explicação sobre o imposto")


class InvoiceAnalysisResponse(BaseModel):
    """Resposta completa da análise de nota fiscal."""
    report: str = Field(
        ...,
        description="Relatório em linguagem natural gerado pela IA explicando os impostos",
    )
    structured_data: dict = Field(
        ...,
        description="Dados estruturados extraídos da nota fiscal",
    )
    valor_total_extenso: str = Field(
        "",
        description="Valor total da nota por extenso",
    )
