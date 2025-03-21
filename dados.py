# dados.py
import pandas as pd

def ler_csv(caminho_csv):
    try:
        df = pd.read_csv(caminho_csv, sep=";")
        alunos = df.to_dict(orient="records")
        return alunos
    except Exception as e:
        print(f"Erro ao ler CSV: {e}")
        return []
