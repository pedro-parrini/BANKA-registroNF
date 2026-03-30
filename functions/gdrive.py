import io
import streamlit as st
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
from google.oauth2.service_account import Credentials
from functions.gsheets import GCP_CREDENTIALS

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

DRIVE_FOLDER_ID = "0AMx_YQjS-FVIUk9PVA"
NOME_PLANILHA   = "Banka l Planilha Gerencial.xlsx"
CAMINHO_LOCAL   = "Banka l Planilha Gerencial.xlsx"


@st.cache_resource
def get_drive_service():
    """Autentica e retorna o serviço do Google Drive."""
    creds = Credentials.from_service_account_info(GCP_CREDENTIALS, scopes=SCOPES)
    return build("drive", "v3", credentials=creds)


def _get_file_id() -> str | None:
    """
    Busca o file ID da planilha gerencial.
    Suporta tanto pastas normais quanto Shared Drives.
    """
    service = get_drive_service()

    # Tenta primeiro como pasta normal
    query = (
        f"name = '{NOME_PLANILHA}' "
        f"and '{DRIVE_FOLDER_ID}' in parents "
        f"and trashed = false"
    )
    resultado = service.files().list(
        q=query,
        fields="files(id, name)",
        includeItemsFromAllDrives=True,
        supportsAllDrives=True,
    ).execute()

    arquivos = resultado.get("files", [])
    if arquivos:
        return arquivos[0]["id"]

    # Fallback: busca pelo nome em todo o Drive acessível pela service account
    query_geral = f"name = '{NOME_PLANILHA}' and trashed = false"
    resultado2 = service.files().list(
        q=query_geral,
        fields="files(id, name)",
        includeItemsFromAllDrives=True,
        supportsAllDrives=True,
    ).execute()

    arquivos2 = resultado2.get("files", [])
    return arquivos2[0]["id"] if arquivos2 else None


def baixar_planilha() -> bool:
    """
    Baixa a planilha gerencial do Google Drive para o servidor local.
    Retorna True se bem-sucedido.
    """
    service = get_drive_service()
    file_id = _get_file_id()

    if not file_id:
        raise FileNotFoundError(f"'{NOME_PLANILHA}' não encontrada no Google Drive.")

    request    = service.files().get_media(fileId=file_id, supportsAllDrives=True)
    buffer     = io.BytesIO()
    downloader = MediaIoBaseDownload(buffer, request)

    done = False
    while not done:
        _, done = downloader.next_chunk()

    buffer.seek(0)
    with open(CAMINHO_LOCAL, "wb") as f:
        f.write(buffer.read())

    return True


def subir_planilha(caminho_local: str = CAMINHO_LOCAL) -> bool:
    """
    Sobe a planilha gerencial para o Google Drive, substituindo a versão anterior.
    Retorna True se bem-sucedido.
    """
    service = get_drive_service()
    file_id = _get_file_id()

    mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    with open(caminho_local, "rb") as f:
        buffer = io.BytesIO(f.read())

    media = MediaIoBaseUpload(buffer, mimetype=mime, resumable=True)

    if file_id:
        # Atualiza o arquivo existente
        service.files().update(
            fileId=file_id,
            media_body=media,
            supportsAllDrives=True,
        ).execute()
    else:
        # Cria novo arquivo na pasta
        metadata = {
            "name":    NOME_PLANILHA,
            "parents": [DRIVE_FOLDER_ID],
        }
        service.files().create(
            body=metadata,
            media_body=media,
            fields="id",
            supportsAllDrives=True,
        ).execute()

    return True


def ler_planilha_bytes() -> bytes:
    """
    Retorna o conteúdo da planilha gerencial como bytes,
    para uso direto no st.download_button sem salvar localmente.
    """
    service = get_drive_service()
    file_id = _get_file_id()

    if not file_id:
        raise FileNotFoundError(f"'{NOME_PLANILHA}' não encontrada no Google Drive.")

    request    = service.files().get_media(fileId=file_id, supportsAllDrives=True)
    buffer     = io.BytesIO()
    downloader = MediaIoBaseDownload(buffer, request)

    done = False
    while not done:
        _, done = downloader.next_chunk()

    buffer.seek(0)
    return buffer.read()
