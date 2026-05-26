"""
Preditores selecionados para o modelo LTFU de tuberculose.
Importar este módulo nos scripts de treino e pipeline.
"""

# Preditores numéricos
PREDITORES_NUMERICOS = [
    "idade_anos",   # Idade do paciente em anos
    "NU_CONTATO",   # Número de contatos registrados
]

# Preditores categóricos
PREDITORES_CATEGORICOS = [
    "CS_SEXO",      # Sexo (M/F/I)
    "CS_RACA",      # Raça/Cor
    "HIV",          # Sorologia HIV
    "BACILOSC_E",   # Baciloscopia de entrada
    "RAIOX_TORA",   # Raio-X de tórax
    "TRATAMENTO",   # Tipo de tratamento (caso novo, recidiva...)
    "SG_UF_NOT",    # UF de notificação (alta cardinalidade → TargetEncoder)
]

# Preditores ordinais
PREDITORES_ORDINAIS = [
    "CS_ESCOL_N",   # Escolaridade (0=sem escolaridade ... 5=superior)
]

# Preditores binários (1=Sim, 2=Não, 9=Ignorado) 
# Serão tratados como categóricos após remap 9→NaN
PREDITORES_BINARIOS = [
    "TRAT_SUPER",   # Tratamento supervisionado (DOT)
    "INSTITUCIO",   # Institucionalizado
    "AGRAVAIDS",    # Comorbidade AIDS
    "AGRAVALCOO",   # Uso de álcool
    "AGRAVDIABE",   # Diabetes
    "AGRAVDOENC",   # Doença mental
    "AGRAVDROGA",   # Uso de drogas ilícitas
    "AGRAVTABAC",   # Tabagismo
    "POP_LIBER",    # Privado de liberdade
    "POP_RUA",      # Situação de rua
    "BENEF_GOV",    # Benefício governamental
]

# Lista unificada para uso no pipeline
TODOS_PREDITORES = (
    PREDITORES_NUMERICOS
    + PREDITORES_CATEGORICOS
    + PREDITORES_ORDINAIS
    + PREDITORES_BINARIOS
)

# Variável-alvo
ALVO = "ltfu"

# Thresholds de risco
THRESHOLD_BAIXO = 0.30   # < 30% → Baixo
THRESHOLD_ALTO = 0.60    # > 60% → Alto

THRESHOLD_CLASSIFICACAO = 0.24  # threshold de decisao binaria (recall ~87% no teste2)
# entre 30% e 60% → Médio

# Colunas de saída do modelo (para o siteDados)
COLUNAS_SAIDA = [
    "id",
    "probabilidade_ltfu",
    "nivel_risco",
    "predicao_modelo",
    "resultado_real",
]
