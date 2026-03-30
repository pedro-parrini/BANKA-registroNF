import pandas as pd
from functions.gsheets import get_lancamentos_para_merge, limpar_aba
from functions.gdrive  import baixar_planilha, subir_planilha, CAMINHO_LOCAL

COLUNAS = [
    "ID number",
    "Data 1 (lançamento pgto)",
    "Data 2 (dia do pgto)",
    "Fornecedor",
    "Banca",
    "Família",
    "Custo de Aquisição",
    "Tipo",
]


def sincronizar_para_gerencial():
    """
    1. Baixa a planilha gerencial do Google Drive
    2. Lê os lançamentos válidos do Google Sheets
    3. Remove cancelados e adiciona novos na aba 'Controle de NFs Tomadas'
    4. Sobe a planilha atualizada de volta ao Google Drive
    5. Limpa as abas auxiliares do Google Sheets

    Retorna o número de lançamentos sincronizados.
    """

    # 1 — Baixar do Drive
    baixar_planilha()

    # 2 — Ler lançamentos do Google Sheets
    lancamentos_validos, ids_cancelados = get_lancamentos_para_merge()

    if not lancamentos_validos and not ids_cancelados:
        return 0

    # 3 — Atualizar a planilha local
    df_atual = pd.read_excel(CAMINHO_LOCAL, sheet_name="Controle de NFs Tomadas")

    if ids_cancelados:
        df_atual = df_atual[~df_atual["ID number"].astype(str).isin(ids_cancelados)]

    if lancamentos_validos:
        df_novos = pd.DataFrame(lancamentos_validos, columns=COLUNAS)
        df_final = pd.concat([df_atual, df_novos], ignore_index=True)
    else:
        df_final = df_atual

    with pd.ExcelWriter(CAMINHO_LOCAL, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
        df_final.to_excel(writer, sheet_name="Controle de NFs Tomadas", index=False)

    # 4 — Subir de volta ao Drive
    subir_planilha()

    # 5 — Limpar abas do Google Sheets
    for aba in ["BaixoGavea", "SaoConrado", "Tijuca", "Cancelamentos"]:
        limpar_aba(aba)

    return len(lancamentos_validos)
