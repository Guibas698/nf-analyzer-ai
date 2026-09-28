# 📄 NF Analyzer AI

Um analisador inteligente de Notas Fiscais (NF-e/NFS-e) rodando 100% localmente. Utiliza LLMs open-source (via Ollama) para extrair dados da nota e redigir um relatório detalhado por extenso sobre quais impostos (ICMS, ISS, IPI, PIS, COFINS) devem ser pagos.

## 🚀 Como Executar

### 1. Iniciar os containers
```bash
docker-compose up -d --build
```

### 2. Baixar o modelo local de IA (Llama 3 ou Mistral)
Como o sistema é 100% local, você precisa baixar o modelo dentro do container do Ollama:
```bash
docker exec -it nf-ollama ollama run llama3
# ou
# docker exec -it nf-ollama ollama run mistral
```

### 3. Acessar
- **Interface UI (Streamlit)**: http://localhost:8501
- **API (FastAPI)**: http://localhost:8000/docs

## 🧠 Arquitetura
1. **Frontend**: Streamlit (Upload de NFs em texto ou imagem simulada).
2. **Backend**: FastAPI + LangChain.
3. **IA Local**: Ollama rodando um modelo avançado para processamento de linguagem natural (NPL) privado.
