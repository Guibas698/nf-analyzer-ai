import streamlit as st
import requests
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="NF Analyzer AI", page_icon="📄", layout="wide")

st.title("📄 Inteligência Fiscal - NF Analyzer")
st.markdown("Faça o upload de uma Nota Fiscal para que a Inteligência Artificial local (Ollama) extraia e explique detalhadamente, por extenso, quais impostos devem ser recolhidos.")

nf_text_input = st.text_area("Cole o conteúdo do XML ou texto da Nota Fiscal (Simulação OCR):", height=250)

if st.button("Analisar Nota Fiscal 🧠"):
    if nf_text_input.strip():
        with st.spinner("A IA está analisando os impostos localmente... Isso pode levar alguns segundos."):
            try:
                response = requests.post(f"{API_URL}/api/analyze", json={"text": nf_text_input})
                
                if response.status_code == 200:
                    data = response.json()
                    st.success("Análise concluída com sucesso!")
                    
                    st.subheader("📋 Relatório Tributário Detalhado")
                    st.markdown(data.get("report", "Nenhum relatório gerado."))
                    
                    st.subheader("💡 Dados Estruturados Extraídos")
                    st.json(data.get("structured_data", {}))
                else:
                    st.error(f"Erro na API: {response.text}")
            except Exception as e:
                st.error(f"Erro ao conectar com a API Backend: {e}")
    else:
        st.warning("Por favor, insira o texto da Nota Fiscal antes de analisar.")

st.markdown("---")
st.caption("🔒 100% Local e Privado - Seus dados fiscais não saem da sua máquina. Processamento via Ollama.")
