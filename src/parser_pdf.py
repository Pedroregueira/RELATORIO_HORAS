import pdfplumber
import pandas as pd
import re

def converter_horas_para_decimal(hora_str):
    horas, minutos = hora_str.split(":")
    return round(int(horas) + int(minutos) / 60, 2)

def extrair_dados_pdf(file):
    # lógica de leitura e extração
    ...
    return df
