import pdfplumber
import pandas as pd
import re


def converter_horas_para_decimal(hora_str):
    horas, minutos = hora_str.split(":")
    return round(int(horas) + int(minutos) / 60, 2)


def extrair_dados_pdf(file):

    dados = []

    with pdfplumber.open(file) as pdf:
        texto = ""
        for pagina in pdf.pages:
            texto += pagina.extract_text() + "\n"

    linhas = texto.split("\n")

    periodo_match = re.search(r"Período de (\d{2}/\d{2}/\d{4}) a (\d{2}/\d{2}/\d{4})", texto)

    if not periodo_match:
        raise ValueError("Período não encontrado no PDF.")

    periodo_inicio = periodo_match.group(1)
    periodo_fim = periodo_match.group(2)
    competencia = periodo_inicio[3:10]

    projeto_atual = None
    tarefa_atual = None

    for linha in linhas:

        linha = linha.strip()

        if linha.startswith("Projeto:"):
            projeto_atual = linha.replace("Projeto:", "").split("|")[0].strip()

        elif linha.startswith("Tarefa:"):
            tarefa_bruta = linha.replace("Tarefa:", "").strip()
            tarefa_atual = re.sub(r"\s\d{1,3}:\d{2}\s[\d\.,]+$", "", tarefa_bruta)

        else:
            match = re.match(r"^([A-ZÁÉÍÓÚÃÕÂÊÔÇ\s]+)\s+(\d{1,3}:\d{2})\s+[\d\.,]+$", linha)

            if match and projeto_atual and tarefa_atual:
                nome = match.group(1).strip()
                horas_str = match.group(2)
                horas_decimal = converter_horas_para_decimal(horas_str)

                dados.append({
                    "competencia": competencia,
                    "periodo_inicio": periodo_inicio,
                    "periodo_fim": periodo_fim,
                    "projeto": projeto_atual,
                    "tarefa": tarefa_atual,
                    "colaborador": nome,
                    "horas": horas_decimal
                })

    df = pd.DataFrame(dados)
    return df
