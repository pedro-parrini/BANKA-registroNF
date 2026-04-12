import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# Escopos necessários
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

SHEET_ID = "1tz-vW9VnLyqpHn9fz8PiCnrKzrQSQxRlMkadrEu_TtI"

# Mapeamento de loja para nome da aba
ABA_POR_LOJA = {
    "Baixo Gávea": "BaixoGavea",
    "São Conrado": "SaoConrado",
    "Tijuca": "Tijuca",
}

GCP_CREDENTIALS = {
    "type": "service_account",
    "project_id": "banka-system",
    "private_key_id": "a033810a7c5e069b3d4311efaed22452642845cb",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDaGWdtx0Gh7Kvz\nhfr+8nMwx2FK6ZRrrZ/bWwSC6cYU86Z8/dj7TD9GmwRejGW4QAHFeWO8W0q5iprY\nGU4QQh/rFCzltIOBA88toVLMd3MvsV9JN2v2MPr4o6gFGk6B1Jp6kGy4Igwnjvsv\nQV/3IY+vfuVJUoIkxD7rjipSaQz2XsnboqruOotvxaOCc77bD+O74MjsixmfB44z\nEuTemOicDgZDN4RosT1cyJs6UvTNb8ylqvYbyvco7TEY41k3T5xSxVjDH/Nd1Hm+\nMW5XxInjVZhdPlYlFUsVRoGogWQZ+YiTGGhf1glg7keKq1JeJd+UyTNYU3rOXZV4\nST7hvqTdAgMBAAECggEAHwESg3gae+7dqOJIgpqrxmjpi1E2QLJvcar4MrYR6yOR\n7N3XTS4TJrHdxqUVxsIOnmh5xaqCrmqmRYcfYk9MI0p8cXEeaqZEevuefiOS89o2\nrf1bcyWWX+c/+O268FjtVvQWCH0KlksMqTSVdFfIic2zwZ8hkiF1wl205X86kQE4\nZyeSwb+d4MJaLOwle3Yo/9Pi5tS0sZA3WhQWtoOsfm0LYrv0sBU+jcMYIvWYF+/L\n8B2ztRVWf7pCZZITvmSrr+tBKT7s6q2DDA61MN/lTNcrwyV1IVQErrBQ8ALC+gIv\nS5w2hoDV4W/APZFZKCuxLoEAj+l6q9Oohnl6SW3OUQKBgQDwLGJ2A6niKSEqD36p\n7DkgjZHJZhEg5qny6OsfZC+P4A1RJy1MQxDudAEV7TQ34wPkzBMIG6CopEr7BvH5\ngxEfNp3UKsISLHHjUbDV+hdTnI4FBv/ldHZ25Hy3oZaSvF7X5smCk7Jzpq4UHg4J\nUbrI8Gs+SPMrW3Pk463lYTAutQKBgQDoeKOAWUAejlcgEaJ8MVwL0dWGVz0UUIc9\nAQ0qILLSqnT4/JFtd5vr9draty3niI+ofODgD7d1qK2HXmpL5KYwX/VQLj5pqQNb\nH8bA9mzW9kwEbZum842WB4Qg7m3D5Njg5x/5mmvQd+MyP2kSGv/mezMhexbfbQYC\nklN5L+DOiQKBgQCRXhv+WDtUExbqsVQ2Hy94n5d08h09778/snDVoDsVd0Q4MWE+\nfn1aBsa9ccQga3xo2IhQaQB18nMbu1lsb0NGxDUFPRgYDeSk9UX2TZge2GwxaMos\nJLCrR6KhNuG/UNqLDTo8mY7yZxmIPaS7SUen5bTTjy33uTPNf206n/ec3QKBgQDM\nqjk4LFtZC3QFFcF5mXMyLMDSD0gE9Ii72osehb8p3UwyURovx9gMO108pXzSlNX1\nPkw0t2GLQr/Tp/npaxotCK5OswfbuiLsPOOcytczwY9XbrBUoaQLa/6Vh5Q3nOib\nyJ/L/nnhBUuO12jHueGFpv1zAo02kyNxbCX1UYOYEQKBgF9jRIHhV4nfNKiMmpB4\nnHajEtRAwQ9q7GclWVDlIUV448PGIHudW3PyLaNR4A+iJjSXH9IUL4J869iOkwzJ\n33kVf2Rk1oS5gpyxPNi8ze5IC7ESoB2nWzW/+vH5VMvsz2mo08PQnZWfg2HgE9ot\n71Br/EtyTlON859M5j/92ukT\n-----END PRIVATE KEY-----\n",
    "client_email": "banka-sheets@banka-system.iam.gserviceaccount.com",
    "client_id": "101962775323057450934",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/banka-sheets%40banka-system.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com",
}

@st.cache_resource
def get_client():
    """Autentica e retorna o cliente gspread. Cached para não reautenticar a cada rerun."""
    creds = Credentials.from_service_account_info(
        GCP_CREDENTIALS,
        scopes=SCOPES,
    )
    return gspread.authorize(creds)


def get_sheet(aba: str):
    """Retorna a worksheet pelo nome da aba."""
    client = get_client()
    spreadsheet = client.open_by_key(SHEET_ID)
    return spreadsheet.worksheet(aba)


def append_lancamento(loja: str, dados: dict):
    """
    Adiciona uma linha de lançamento na aba da loja correspondente.
    Usa append_row para evitar sobreposição em acessos simultâneos.
    """
    aba = ABA_POR_LOJA[loja]
    sheet = get_sheet(aba)

    linha = [
        dados.get("ID number", ""),
        dados.get("Data 1 (lançamento pgto)", ""),
        dados.get("Data 2 (dia do pgto)", ""),
        dados.get("Fornecedor", ""),
        dados.get("Banca", ""),
        dados.get("Família", ""),
        float(dados.get("Custo de Aquisição", 0) or 0),
        dados.get("Tipo", ""),
    ]

    sheet.append_row(linha, value_input_option="USER_ENTERED")


def append_cancelamento(id_number: str):
    """Adiciona um ID na aba de Cancelamentos."""
    sheet = get_sheet("Cancelamentos")
    sheet.append_row([id_number], value_input_option="USER_ENTERED")


def append_fornecedor(dados: dict):
    """Adiciona um fornecedor na aba de Fornecedores."""
    sheet = get_sheet("Fornecedores")
    linha = [
        dados.get("Fornecedores", ""),
        dados.get("CNPJ", ""),
        dados.get("Contato", ""),
    ]
    sheet.append_row(linha, value_input_option="USER_ENTERED")


def get_fornecedores() -> list:
    """Retorna lista de nomes de fornecedores cadastrados."""
    sheet = get_sheet("Fornecedores")
    registros = sheet.get_all_records()
    return [r["Fornecedores"] for r in registros if r.get("Fornecedores")]


def get_ids_existentes() -> list:
    """Retorna todos os IDs já registrados nas 3 bancas."""
    ids = []
    for aba in ["BaixoGavea", "SaoConrado", "Tijuca"]:
        sheet = get_sheet(aba)
        registros = sheet.get_all_records()
        ids += [str(r.get("ID number", "")) for r in registros if r.get("ID number")]
    return ids


COLUNAS_LANCAMENTO = [
    "ID number",
    "Data 1 (lançamento pgto)",
    "Data 2 (dia do pgto)",
    "Fornecedor",
    "Banca",
    "Família",
    "Custo de Aquisição",
    "Tipo",
]


def get_lancamentos_para_merge() -> list:
    """
    Retorna todos os lançamentos das 3 bancas e os IDs a cancelar.
    Usa get_all_values() em vez de get_all_records() para evitar
    conversão automática incorreta de números decimais pelo gspread.
    Retorna: (lista de dicts com lançamentos, lista de IDs para cancelar)
    """
    lancamentos = []
    for aba in ["BaixoGavea", "SaoConrado", "Tijuca"]:
        sheet = get_sheet(aba)
        rows = sheet.get_all_values()
        if len(rows) <= 1:
            continue  # Só cabeçalho ou vazia

        cabecalho = rows[0]
        for row in rows[1:]:
            registro = dict(zip(cabecalho, row))

            # Converter Custo de Aquisição para float preservando decimais
            custo_raw = registro.get("Custo de Aquisição", "0")
            try:
                # Substitui vírgula por ponto caso venha no formato brasileiro
                registro["Custo de Aquisição"] = float(str(custo_raw).replace(",", "."))
            except (ValueError, TypeError):
                registro["Custo de Aquisição"] = 0.0

            lancamentos.append(registro)

    sheet_cancel = get_sheet("Cancelamentos")
    rows_cancel = sheet_cancel.get_all_values()
    cancelamentos = [row[0] for row in rows_cancel[1:] if row and row[0]]

    # Filtrar lançamentos removendo os cancelados
    lancamentos_validos = [
        l for l in lancamentos
        if str(l.get("ID number", "")) not in cancelamentos
    ]

    return lancamentos_validos, cancelamentos


def limpar_aba(aba: str):
    """
    Limpa todos os dados de uma aba mantendo o cabeçalho (linha 1).
    Usado após sincronização.
    """
    sheet = get_sheet(aba)
    # Pega número de linhas atuais
    todos = sheet.get_all_values()
    if len(todos) <= 1:
        return  # Só tem cabeçalho ou está vazia, nada a fazer

    # Deleta da linha 2 até o final
    sheet.delete_rows(2, len(todos))
