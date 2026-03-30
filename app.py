# ── Imports ──────────────────────────────────────────────────────────────────
import os
import pytz
import time
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime

from functions.id_generate      import id_number
from functions.boleto_date      import obter_data_vencimento
from functions.boleto_validate  import validar_boleto
from functions.boleto_value     import obter_valor_boleto
from functions.mail_boleto      import enviar_email_boleto
from functions.mail_pix         import enviar_email_pix
from functions.mail_id_remove   import email_id_remove
from functions.cnpj_validate    import validar_cnpj
from functions.cnpj_format      import formatar_cnpj
from functions.current_date     import data_atual
from functions.excel_backup     import backup_planilha
from functions.excel_merge      import sincronizar_para_gerencial
from functions.gdrive           import baixar_planilha, subir_planilha, ler_planilha_bytes
from functions.folder_create    import criar_pasta
from functions.folder_delete    import apagar_pasta
from functions.gsheets          import (
    append_lancamento,
    append_cancelamento,
    append_fornecedor,
    get_fornecedores,
)

# ── Configuração da página ────────────────────────────────────────────────────
st.set_page_config(
    page_title="BANKA",
    page_icon="💰",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.title(":green[BANKA - Registro de Compras]")

# ── Constantes ────────────────────────────────────────────────────────────────
SENHA_ADMIN = "Novembro.2024"

DESTINATARIOS_PADRAO = [
    "pedro.parrini@equityrio.com.br",
    "brunodnpeniche@gmail.com",
    "financeiro.banka@gmail.com",
    "gerencia.banka@gmail.com",
]

EMAIL_POR_LOJA = {
    "Baixo Gávea":  "bankagavea@gmail.com",
    "São Conrado":  "bankasaoconrado@gmail.com",
    "Tijuca":       "bankatijuca@gmail.com",
}

PLANILHA_GERENCIAL = "Banka l Planilha Gerencial.xlsx"

FAMILIAS = [
    "", "Bebidas", "Bomboniere", "Cigarros", "Diversos",
    "Jornais", "Livros", "Revistas", "Sorvetes", "Tabacaria",
]

LOJAS = ["Baixo Gávea", "São Conrado", "Tijuca"]

# ── Fuso horário ──────────────────────────────────────────────────────────────
brazil_tz    = pytz.timezone("America/Sao_Paulo")
current_time = datetime.now(brazil_tz)
current_hour = current_time.hour

# ── Menu lateral ──────────────────────────────────────────────────────────────
st.sidebar.title("Menu")
option = st.sidebar.selectbox(
    "Escolha uma opção:",
    ("Lançamento de Compras", "Controle Operacional", "Cancelar Lançamento",
     "Cadastrar Fornecedores", "Resultados"),
)

# ══════════════════════════════════════════════════════════════════════════════
# 1 ─ LANÇAMENTO DE COMPRAS
# ══════════════════════════════════════════════════════════════════════════════
if option == "Lançamento de Compras":

    if not (13 <= current_hour < 20):
        st.error("Acesso restrito! Esta aba pode ser acessada entre 13:00 e 20:00 no horário do Brasil.")

    else:
        loja          = st.radio("Selecione a loja em que você trabalha:", LOJAS)
        tipo_registro = st.radio("Qual tipo de registro você quer fazer?", ["Boleto", "PIX"])

        email_funcionario = st.text_input(
            "Digite seu email para receber o registro em cópia:",
            value=EMAIL_POR_LOJA.get(loja, ""),
        )

        lista_fornecedores = [""] + get_fornecedores()

        # ── BOLETO ────────────────────────────────────────────────────────────
        if tipo_registro == "Boleto":

            nota_upload   = st.file_uploader("*Nota Fiscal ou Recibo de Compra (PDF ou Foto Escaneada)", type=["pdf", "jpg", "jpeg", "png"])
            numero_nota   = st.text_input("*Número da Nota:")
            boleto_upload = st.file_uploader("*Boleto (PDF ou Foto Escaneada)", type=["pdf", "jpg", "jpeg", "png"])
            numero_boleto = st.text_input("*Número do Boleto:").replace(" ", "").replace(".", "").replace("-", "")
            xml_upload    = st.file_uploader("XML da Nota Fiscal", type=["xml"])
            fornecedor    = st.selectbox("*Fornecedor:", lista_fornecedores)
            familia       = st.selectbox("*Família:", FAMILIAS)
            valor_boleto  = st.number_input("*Valor do Boleto (BRL):", value=obter_valor_boleto(numero_boleto))
            data_venc     = st.date_input("*Data de Vencimento do Boleto (AAAA/MM/DD)", value=obter_data_vencimento(numero_boleto))
            comentarios   = st.text_input("Observações:")

            if st.button(f"Registrar Informações - {loja}"):

                campos_ok = all([loja, email_funcionario, nota_upload, numero_nota,
                                 boleto_upload, numero_boleto, fornecedor, familia,
                                 valor_boleto, data_venc])

                if not campos_ok:
                    st.error("Por favor, preencha todos os campos obrigatórios.")

                elif not validar_boleto(numero_boleto):
                    st.error("O número do boleto é inválido.")

                else:
                    try:
                        data_venc_str         = data_venc.strftime("%d/%m/%Y")
                        valor_boleto_formatado = f"R$ {valor_boleto}"
                        destinatarios         = [email_funcionario] + DESTINATARIOS_PADRAO
                        codigo_id             = id_number()

                        # Salvar arquivos temporariamente
                        criar_pasta("uploads")
                        nota_path = os.path.join("uploads", nota_upload.name)
                        with open(nota_path, "wb") as f:
                            f.write(nota_upload.getbuffer())

                        boleto_path = os.path.join("uploads", boleto_upload.name)
                        with open(boleto_path, "wb") as f:
                            f.write(boleto_upload.getbuffer())

                        xml_path = "sem_xml"
                        if xml_upload:
                            xml_path = os.path.join("uploads", xml_upload.name)
                            with open(xml_path, "wb") as f:
                                f.write(xml_upload.getbuffer())

                        # Salvar no Google Sheets
                        novo_lancamento = {
                            "ID number":                codigo_id,
                            "Data 1 (lançamento pgto)": data_atual(),
                            "Data 2 (dia do pgto)":     data_venc_str,
                            "Fornecedor":               fornecedor,
                            "Banca":                    loja,
                            "Família":                  familia,
                            "Custo de Aquisição":       float(valor_boleto),
                            "Tipo":                     tipo_registro,
                        }
                        append_lancamento(loja, novo_lancamento)

                        # Enviar e-mail
                        enviar_email_boleto(
                            tipo_registro, loja, fornecedor, numero_nota,
                            data_venc_str, valor_boleto_formatado, numero_boleto,
                            comentarios, nota_path, boleto_path, xml_path,
                            destinatarios, codigo_id,
                        )

                        apagar_pasta("uploads")
                        st.success(f"Registro salvo com sucesso! Código de identificação: **{codigo_id}**")

                    except Exception as e:
                        st.error(f"Erro ao registrar lançamento: {e}")

        # ── PIX ───────────────────────────────────────────────────────────────
        elif tipo_registro == "PIX":

            chave_pix      = st.text_input("*Chave PIX:")
            valor_pix      = st.number_input("*Valor do Pagamento (BRL):")
            arquivo_upload = st.file_uploader("*Nota Fiscal ou Recibo de Compra (PDF ou Foto Escaneada)", type=["pdf", "jpg", "jpeg", "png"])
            data_venc      = st.date_input("*Data de Vencimento:")
            fornecedor     = st.selectbox("*Fornecedor:", lista_fornecedores)
            familia        = st.selectbox("*Família:", FAMILIAS)
            comentarios    = st.text_input("Observações:")

            if st.button(f"Registrar Informações - {loja}"):

                campos_ok = all([loja, email_funcionario, chave_pix, valor_pix,
                                 arquivo_upload, data_venc, fornecedor, familia])

                if not campos_ok:
                    st.error("Por favor, preencha todos os campos obrigatórios.")

                else:
                    try:
                        data_venc_str     = data_venc.strftime("%d/%m/%Y")
                        valor_pix_fmt     = f"R$ {valor_pix}"
                        destinatarios     = [email_funcionario] + DESTINATARIOS_PADRAO
                        codigo_id         = id_number()

                        criar_pasta("uploads")
                        arquivo_path = os.path.join("uploads", arquivo_upload.name)
                        with open(arquivo_path, "wb") as f:
                            f.write(arquivo_upload.getbuffer())

                        novo_lancamento = {
                            "ID number":                codigo_id,
                            "Data 1 (lançamento pgto)": data_atual(),
                            "Data 2 (dia do pgto)":     data_venc_str,
                            "Fornecedor":               fornecedor,
                            "Banca":                    loja,
                            "Família":                  familia,
                            "Custo de Aquisição":       float(valor_pix),
                            "Tipo":                     tipo_registro,
                        }
                        append_lancamento(loja, novo_lancamento)

                        enviar_email_pix(
                            tipo_registro, loja, chave_pix, valor_pix_fmt,
                            data_venc_str, fornecedor, comentarios,
                            arquivo_path, destinatarios, codigo_id,
                        )

                        apagar_pasta("uploads")
                        st.success(f"Registro salvo com sucesso! Código de identificação: **{codigo_id}**")

                    except Exception as e:
                        st.error(f"Erro ao registrar lançamento: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# 2 ─ CONTROLE OPERACIONAL
# ══════════════════════════════════════════════════════════════════════════════
elif option == "Controle Operacional":

    password = st.text_input("Digite a senha para acessar a área restrita:", type="password")

    if password == SENHA_ADMIN:

        st.success("Senha correta! Agora, você tem acesso à planilha gerencial da Banka.")

        # ── Sincronizar ───────────────────────────────────────────────────────
        st.subheader("Sincronizar o Sistema")
        st.caption("Puxa todos os lançamentos do Google Sheets e adiciona na planilha gerencial.")

        if st.button("🔄 Sincronizar o Sistema"):
            try:
                qtd = sincronizar_para_gerencial()
                if qtd == 0:
                    st.info("Nenhum lançamento novo para sincronizar.")
                else:
                    st.success(f"{qtd} lançamento(s) sincronizado(s) com sucesso!")
            except Exception as e:
                st.error(f"Erro na sincronização: {e}")

        st.divider()

        # ── Download da planilha gerencial (vem do Drive) ─────────────────────
        st.subheader("Baixar a Planilha Existente")
        try:
            dados_planilha = ler_planilha_bytes()
            st.download_button(
                label="📥 Baixar Planilha Gerencial",
                data=dados_planilha,
                file_name="Banka l Planilha Gerencial.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        except Exception as e:
            st.error(f"Erro ao buscar planilha do Drive: {e}")

        st.divider()

        # ── Upload de nova planilha (salva no Drive) ──────────────────────────
        st.subheader("Salvar Nova Planilha")
        uploaded_file = st.file_uploader("Selecione a planilha da Banka mais recente", type=["xlsx"])

        if uploaded_file is not None:
            try:
                with open(PLANILHA_GERENCIAL, "wb") as file:
                    file.write(uploaded_file.getbuffer())
                subir_planilha()
                backup_planilha(PLANILHA_GERENCIAL)
                st.success("Planilha enviada e salva no Google Drive com sucesso!")
            except Exception as e:
                st.error(f"Erro ao processar o arquivo: {e}")

    elif password:
        st.error("Senha incorreta. Tente novamente.")

# ══════════════════════════════════════════════════════════════════════════════
# 3 ─ CANCELAR LANÇAMENTO
# ══════════════════════════════════════════════════════════════════════════════
elif option == "Cancelar Lançamento":

    todos_emails = [
        "",
        "pedro.parrini@equityrio.com.br",
        "brunodnpeniche@gmail.com",
        "financeiro.banka@gmail.com",
        "gerencia.banka@gmail.com",
        "bankagavea@gmail.com",
        "bankasaoconrado@gmail.com",
        "bankatijuca@gmail.com",
    ]

    email_funcionario = st.selectbox("*Email para receber o registro em cópia:", todos_emails)
    loja              = st.radio("*Selecione a unidade:", LOJAS)
    id_cancelar       = st.text_input("*ID do lançamento a cancelar:")

    if st.button("Remover Lançamento"):

        if not all([email_funcionario, id_cancelar, loja]):
            st.error("Indique o código que será removido, o email e a unidade para confirmar o cancelamento.")

        else:
            try:
                append_cancelamento(id_cancelar)
                email_id_remove(id_cancelar, email_funcionario, loja)
                st.success("Lançamento cancelado com sucesso! Será removido na próxima sincronização.")
            except Exception as e:
                st.error(f"Erro ao cancelar lançamento: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# 4 ─ CADASTRAR FORNECEDORES
# ══════════════════════════════════════════════════════════════════════════════
elif option == "Cadastrar Fornecedores":

    nome_fornecedor    = st.text_input("*Nome do Fornecedor:")
    cnpj_fornecedor    = st.text_input("CNPJ do Fornecedor:")
    contato_fornecedor = st.text_input("Contato do Fornecedor:")

    if cnpj_fornecedor:
        cnpj_fornecedor = formatar_cnpj(cnpj_fornecedor)
        validar_cnpj(cnpj_fornecedor)

    if st.button("Cadastrar o Fornecedor"):

        if not nome_fornecedor:
            st.error("Por favor, informe o nome do fornecedor.")

        else:
            try:
                append_fornecedor({
                    "Fornecedores": nome_fornecedor,
                    "CNPJ":         cnpj_fornecedor,
                    "Contato":      contato_fornecedor,
                })
                st.success(f"{nome_fornecedor} cadastrado com sucesso!")
            except Exception as e:
                st.error(f"Erro ao cadastrar fornecedor: {e}")