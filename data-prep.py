### Script de Preparação Básica dos Dados ###
"""
Script de preparação dos dados de Tuberculose do SINAN (todos os anos disponíveis)
@Entrada: tuberculose_unificado.feather
@Saída:treino.csv, teste1.csv, teste2.csv
"""

import polars as pl # Polars performa melhor com grande volume de dados

colunas = [
    "NU_IDADE_N", "FORMA", "TRATAMENTO", "POP_RUA", "POP_LIBER", "POP_IMIG", 
    "POP_SAUDE", "CS_GESTANT", "TEST_MOLEC", "TEST_SENSI", "SITUA_ENCE", 
    "DT_NOTIFIC", "NU_CONTATO", "CS_SEXO", "CS_RACA", "HIV", "BACILOSC_E", 
    "RAIOX_TORA", "SG_UF_NOT", "CS_ESCOL_N", "TRAT_SUPER", "INSTITUCIO", 
    "AGRAVAIDS", "AGRAVALCOO", "AGRAVDIABE", "AGRAVDOENC", "AGRAVDROGA", 
    "AGRAVTABAC", "BENEF_GOV"
]
df = pl.scan_ipc("tuberculose_unificado.feather").select(colunas)

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
df = df.collect(streaming=True)

### divisão treino-teste ###
df_train = df.filter(pl.col("DT_NOTIFIC").dt.year() < 2025)
df_teste_ano = df.filter(pl.col("DT_NOTIFIC").dt.year() == 2025)

df_teste_ano = df_teste_ano.sort("DT_NOTIFIC", descending=False)


total_linhas_teste = df_teste_ano.height
test2 = df_teste_ano.tail(20000)
test1 = df_teste_ano.head(total_linhas_teste - 20000)

### exportar conjuntos de treino, teste1 e teste2 ###
df_train.write_csv("treino.csv")
test1.write_csv("teste1.csv")
test2.write_csv("teste2.csv")