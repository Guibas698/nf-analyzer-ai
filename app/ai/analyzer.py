"""Módulo de análise fiscal com LLM local (Ollama).

Utiliza LangChain + Ollama para executar modelos de linguagem
localmente (LLaMA 3, Mistral) sem depender de APIs externas pagas.
100% offline e privado.
"""

import os
import json
import re
import logging
from decimal import Decimal

from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from num2words import num2words

logger = logging.getLogger(__name__)

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
MODEL_NAME = os.getenv("MODEL_NAME", "llama3")


def get_llm() -> Ollama:
    """Cria instância do LLM local via Ollama."""
    return Ollama(
        base_url=OLLAMA_BASE_URL,
        model=MODEL_NAME,
        temperature=0.2,
    )


def valor_por_extenso(valor: float) -> str:
    """Converte valor monetário para texto por extenso em PT-BR.

    Exemplos:
        1234.56 -> 'um mil, duzentos e trinta e quatro reais e cinquenta e seis centavos'
        100.00  -> 'cem reais'
        0.50    -> 'cinquenta centavos'
    """
    try:
        valor_dec = Decimal(str(valor))
        inteiro = int(valor_dec)
        centavos = int(round((valor_dec - inteiro) * 100))

        sufixo_int = " real" if inteiro == 1 else " reais"
        sufixo_dec = " centavo" if centavos == 1 else " centavos"

        texto_int = f"{num2words(inteiro, lang='pt_BR')}{sufixo_int}" if inteiro > 0 else ""
        texto_dec = f"{num2words(centavos, lang='pt_BR')}{sufixo_dec}" if centavos > 0 else ""

        if texto_int and texto_dec:
            return f"{texto_int} e {texto_dec}"
        return texto_int or texto_dec or "zero reais"
    except Exception as e:
        logger.warning(f"Erro ao converter valor por extenso: {e}")
        return f"R$ {valor:.2f}"


def extrair_valores_xml(text: str) -> dict:
    """Tenta extrair valores de tags XML de NF-e (padrão SEFAZ).

    Busca campos como vNF, vICMS, vPIS, vCOFINS, vIPI, etc.
    dentro do XML da nota fiscal.
    """
    campos = {
        "valor_total": r"<vNF>([\d.,]+)</vNF>",
        "valor_icms": r"<vICMS>([\d.,]+)</vICMS>",
        "base_calculo_icms": r"<vBC>([\d.,]+)</vBC>",
        "valor_pis": r"<vPIS>([\d.,]+)</vPIS>",
        "valor_cofins": r"<vCOFINS>([\d.,]+)</vCOFINS>",
        "valor_ipi": r"<vIPI>([\d.,]+)</vIPI>",
        "valor_produtos": r"<vProd>([\d.,]+)</vProd>",
        "valor_frete": r"<vFrete>([\d.,]+)</vFrete>",
        "valor_desconto": r"<vDesc>([\d.,]+)</vDesc>",
        "cnpj_emitente": r"<emit>.*?<CNPJ>(\d+)</CNPJ>",
        "razao_social": r"<xNome>([^<]+)</xNome>",
        "cfop": r"<CFOP>(\d+)</CFOP>",
        "ncm": r"<NCM>(\d+)</NCM>",
    }

    dados = {}
    for campo, pattern in campos.items():
        match = re.search(pattern, text, re.DOTALL)
        if match:
            valor_str = match.group(1)
            # Tenta converter para float se for numérico
            try:
                valor_str_normalizado = valor_str.replace(".", "").replace(",", ".")
                dados[campo] = float(valor_str_normalizado)
            except ValueError:
                dados[campo] = valor_str

    return dados


def analyze_invoice(text: str) -> dict:
    """Pipeline principal de análise de nota fiscal com IA local.

    Etapas:
    1. Extrai dados estruturados do texto/XML
    2. Converte valores para extenso
    3. Envia para o LLM local gerar relatório tributário
    4. Tenta extrair JSON estruturado do LLM

    Args:
        text: Conteúdo da nota fiscal (XML, texto OCR, etc.)

    Returns:
        Dicionário com relatório, dados estruturados e valores por extenso
    """
    llm = get_llm()

    # Etapa 1: Extrair dados do XML/texto
    dados_extraidos = extrair_valores_xml(text)

    # Etapa 2: Converter valores para extenso
    valores_extenso = {}
    for campo, valor in dados_extraidos.items():
        if isinstance(valor, (int, float)) and "valor" in campo:
            valores_extenso[campo] = valor_por_extenso(valor)

    valor_total_extenso = valores_extenso.get(
        "valor_total",
        valor_por_extenso(dados_extraidos.get("valor_total", 0)),
    )

    # Etapa 3: Prompt para o LLM gerar relatório tributário
    report_prompt = PromptTemplate(
        input_variables=["text", "dados_extraidos", "valores_extenso"],
        template="""Você é um auditor fiscal especialista em impostos brasileiros.
Analise o conteúdo da Nota Fiscal abaixo e escreva um relatório COMPLETO e DETALHADO
explicando para o empresário:

1. Quais impostos devem ser pagos (ICMS, PIS, COFINS, IPI, ISS, CSLL, IRPJ)
2. O valor de cada imposto identificado, escrito POR EXTENSO em reais
3. A base de cálculo e alíquota de cada imposto quando disponível
4. Qual o regime tributário mais provável (Simples Nacional, Lucro Presumido, Lucro Real)
5. Observações e recomendações fiscais

Dados extraídos automaticamente da nota:
{dados_extraidos}

Valores por extenso:
{valores_extenso}

Conteúdo original da Nota Fiscal:
{text}

RELATÓRIO TRIBUTÁRIO DETALHADO (em Português do Brasil):""",
    )

    # Etapa 4: Prompt para extrair JSON estruturado
    json_prompt = PromptTemplate(
        input_variables=["text"],
        template="""Analise o texto da nota fiscal e extraia os impostos no formato JSON:
{{"impostos": [{{"nome": "ICMS", "valor": 100.0, "aliquota": "18%"}}, ...],"valor_total": 0.0, "emitente": ""}}

Texto da nota fiscal:
{text}

JSON (apenas o JSON, sem texto adicional):""",
    )

    # Executa o LLM
    try:
        report_text = llm.invoke(
            report_prompt.format(
                text=text[:2000],  # Limita tamanho para o modelo
                dados_extraidos=json.dumps(dados_extraidos, indent=2, ensure_ascii=False),
                valores_extenso=json.dumps(valores_extenso, indent=2, ensure_ascii=False),
            )
        )
    except Exception as e:
        logger.error(f"Erro ao gerar relatório com LLM: {e}")
        report_text = (
            f"⚠️ Erro ao contatar a IA Local (Ollama): {e}\n\n"
            f"Verifique se o modelo '{MODEL_NAME}' está baixado.\n"
            f"Execute: docker exec -it nf-ollama ollama run {MODEL_NAME}\n\n"
            f"--- Dados extraídos automaticamente ---\n"
        )
        for campo, valor in dados_extraidos.items():
            extenso = valores_extenso.get(campo, "")
            report_text += f"• {campo}: {valor}"
            if extenso:
                report_text += f" ({extenso})"
            report_text += "\n"

    # Tenta extrair JSON do LLM
    try:
        json_text = llm.invoke(json_prompt.format(text=text[:2000]))
        match = re.search(r'\{.*\}', json_text, re.DOTALL)
        if match:
            structured_data = json.loads(match.group())
        else:
            structured_data = dados_extraidos
    except Exception:
        structured_data = dados_extraidos

    # Enriquece dados estruturados com valores por extenso
    structured_data["valores_por_extenso"] = valores_extenso

    return {
        "report": report_text,
        "structured_data": structured_data,
        "valor_total_extenso": valor_total_extenso,
    }
