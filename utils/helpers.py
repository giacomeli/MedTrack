import pandas as pd

def load_product_names_from_csv(file_path: str):
    df = pd.read_csv(file_path, delimiter=';', encoding='ISO-8859-1')
    product_names = df['NOME_PRODUTO'].dropna().unique().tolist()
    return product_names
