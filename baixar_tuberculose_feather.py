### script para download dos dados de Tuberculose do SINAN e união em um único DataFrame ###
"""
É preciso instalar o pip install pysus
Ele só funciona em um ambiente WSL, por isso o uso do docker. 
Use a versão 3.10 ou 3.9 do Python. 
"""

import os
from pysus import SINAN
import pandas as pd

def main():
    print("Carregando metadados do SINAN...")
    sinan = SINAN().load()

    print("Buscando arquivos de tuberculose (TUBE)...")
    arquivos = sinan.get_files(dis_code="TUBE")

    if not arquivos:
        print("Nenhum arquivo encontrado para TUBE.")
        return

    # Pasta onde os arquivos serão salvos (montada do Windows)
    pasta_saida = "/data/tuberculose_feather"
    os.makedirs(pasta_saida, exist_ok=True)

    print(f"Salvando arquivos individuais em: {pasta_saida}")

    caminhos = []

    # Baixar cada arquivo
    for arq in arquivos:
        print(f"Baixando: {arq.basename}")
        parquet = arq.download()
        df = parquet.to_dataframe()

        # Nome do arquivo convertido
        nome_feather = arq.basename.replace(".parquet", ".feather")
        caminho = os.path.join(pasta_saida, nome_feather)

        df.to_feather(caminho)
        caminhos.append(caminho)

    print("Unindo todos os arquivos em um único DataFrame...")
    import polars as pl
    df_final = pl.concat([pl.read_ipc(c) for c in caminhos], how="diagonal")
    caminho_final = "/data/tuberculose_unificado.feather"
    df_final.write_ipc(caminho_final)

    print(f"Arquivo final salvo em: {caminho_final}")
    print("Processo concluído com sucesso!")

if __name__ == "__main__":
    main()