import streamlit as st
from parser_pdf import extrair_dados_pdf

st.title("Upload PDF Progad")

uploaded_file = st.file_uploader("Envie o PDF", type="pdf")

if uploaded_file:
    df = extrair_dados_pdf(uploaded_file)
    st.dataframe(df)
