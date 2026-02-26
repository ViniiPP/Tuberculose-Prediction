### Script de Preparação Básica dos Dados ###
"""
Script de preparação dos dados de Tuberculose do SINAN (todos os anos disponíveis)
@Entrada: tuberculose_unificado.feather
@Saída:treino.csv, teste1.csv, teste2.csv
"""

import polars as pl # Polars performa melhor com grande volume de dados

df = pl.read_ipc("tuberculose_unificado.feather")

# limpar strings
df = df.with_columns(
    pl.col(pl.Utf8).str.strip_chars()
)

# padronizações
df = df.with_columns(
    pl.when(pl.col("NU_IDADE_N") == "")
    .then(None)
    .otherwise(pl.col("NU_IDADE_N"))
    .alias("NU_IDADE_N")
)

df = df.with_columns(
    pl.col("NU_IDADE_N").str.slice(0, 1).cast(pl.Int8, strict=False).alias("idade_unid"), # ver a var idade no dicio de dados
    pl.col("NU_IDADE_N").str.slice(1, 3).cast(pl.Int16, strict=False).alias("idade_val"),
)

df = df.with_columns(
    pl.when(pl.col("idade_unid") == 4).then(pl.col("idade_val"))
    .when(pl.col("idade_unid") == 3).then((pl.col("idade_val") / 12).floor())
    .when(pl.col("idade_unid") == 2).then((pl.col("idade_val") / 365).floor())
    .otherwise(None)
    .cast(pl.Int16)
    .alias("idade_anos")
)

# filtros
### é possível modificar os filtros. Eles devem ser escolhidos por razões justificáveis ###
df = (
    df
    .filter(pl.col("idade_anos") >= 18) 
    .filter(pl.col("FORMA") == "1")
    .filter(pl.col("TRATAMENTO") != "6")
    .filter(pl.col("POP_RUA").is_in(["1", "2"]) | pl.col("POP_RUA").is_null())
    .filter(pl.col("POP_LIBER").is_in(["1", "2"]) | pl.col("POP_LIBER").is_null())
    .filter(pl.col("POP_IMIG").is_in(["1", "2"]) | pl.col("POP_IMIG").is_null())
    .filter(pl.col("POP_SAUDE").is_in(["2", "9"]) | pl.col("POP_SAUDE").is_null())
    .filter(pl.col("CS_GESTANT").is_in(["5", "6", "9"]) | pl.col("CS_GESTANT").is_null())
    .filter(~pl.col("TEST_MOLEC").is_in(["2"]))
    .filter(~pl.col("TEST_SENSI").is_in(["1", "2", "3", "4"]))
    .filter(pl.col("SITUA_ENCE") != "7")
    .filter(pl.col("SITUA_ENCE").is_in(["1", "2"]))
)

# preparação da variável-alvo da predição
df = df.with_columns(
    pl.when(pl.col("SITUA_ENCE") == "2").then(1)
    .when(pl.col("SITUA_ENCE") == "1").then(0)
    .otherwise(None)
    .cast(pl.Int8)
    .alias("ltfu")
)

# remover linhas que não correspondam aos valores-alvo
df = df.drop_nulls(subset=["ltfu"])

### divisão treino-teste ###
# a divisão foi realizada com base nas datas
df_train = df.filter(pl.col("DT_NOTIFIC").dt.year() < 2025)
df_teste_ano = df.filter(pl.col("DT_NOTIFIC").dt.year() == 2025)

df_teste_ano = df_teste_ano.sort("DT_NOTIFIC", descending=False)


total_linhas_teste = df_teste_ano.height
ponto_corte = total_linhas_teste // 2

test1= df_teste_ano.head(ponto_corte)
test2 = df_teste_ano.tail(total_linhas_teste - ponto_corte)

### exportar conjuntos de treino, teste1 e teste2 ###
df_train.write_csv("treino.csv")
test1.write_csv("teste1.csv")
test2.write_csv("teste2.csv")