import pdfplumber
import pandas as pd
import re


# ----------------------------------------
# Regra contratual:
# >=30 minutos sobe 1 hora
# <30 minutos mantém a hora
# ----------------------------------------
def converter_horas_para_inteiro(hora_str):
    try:
        horas, minutos = hora_str.split(":")
        horas = int(horas)
        minutos = int(minutos)

        if minutos >= 30:
            return horas + 1
        else:
            return horas

    except Exception:
        return 0  # segurança caso venha formato inesperado


def extrair_dados_pdf(file):

    dados = []

    with pdfplumber.open(file) as pdf:
        texto = ""
        for pagina in pdf.pages:
            texto_extraido = pagina.extract_text()
            if texto_extraido:
                texto += texto_extraido + "\n"

    linhas = texto.split("\n")

    # -------------------------
    # Extrair período
    # -------------------------
    periodo_match = re.search(
        r"Período de (\d{2}/\d{2}/\d{4}) a (\d{2}/\d{2}/\d{4})",
        texto
    )

    if not periodo_match:
        raise ValueError("Período não encontrado no PDF.")

    periodo_inicio = periodo_match.group(1)
    periodo_fim = periodo_match.group(2)
    competencia = periodo_inicio[3:10]  # MM/YYYY

    projeto_atual = None
    tarefa_atual = None

    for linha in linhas:

        linha = linha.strip()

        # -------------------------
        # Detectar Projeto
        # -------------------------
        if linha.startswith("Projeto:"):
            projeto_atual = linha.replace("Projeto:", "").split("|")[0].strip()

        # -------------------------
        # Detectar Tarefa
        # -------------------------
        elif linha.startswith("Tarefa:"):
            tarefa_bruta = linha.replace("Tarefa:", "").strip()

            tarefa_atual = re.sub(
                r"\s\d{1,3}:\d{2}\s[\d\.,]+$",
                "",
                tarefa_bruta
            )

        # -------------------------
        # Detectar Colaboradores
        # -------------------------
        else:
            match = re.match(
                r"^([A-ZÁÉÍÓÚÃÕÂÊÔÇ\s]+)\s+(\d{1,3}:\d{2})\s+[\d\.,]+$",
                linha
            )

            if match and projeto_atual and tarefa_atual:

                nome = match.group(1).strip()
                horas_str = match.group(2)

                horas_faturadas = converter_horas_para_inteiro(horas_str)

                dados.append({
                    "competencia": competencia,
                    "periodo_inicio": periodo_inicio,
                    "periodo_fim": periodo_fim,
                    "projeto": projeto_atual,
                    "tarefa": tarefa_atual,
                    "colaborador": nome,
                    "horas_formatada": horas_str,
                    "horas_faturadas": horas_faturadas
                })

    df = pd.DataFrame(dados)

    # ----------------------------------------
    # GARANTIA DEFINITIVA DE TIPO NUMÉRICO
    # ----------------------------------------
    df["horas_faturadas"] = pd.to_numeric(
        df["horas_faturadas"],
        errors="coerce"
    ).fillna(0).astype(int)

    return df
