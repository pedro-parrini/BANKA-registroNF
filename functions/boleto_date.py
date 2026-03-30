from datetime import datetime, timedelta

# Data base original: 07/10/1997
# Em 21/02/2025 o fator atingiu 9999 (máximo de 4 dígitos)
# A partir de 22/02/2025 (FEBRABAN FB-009/2023), o fator reinicia em 1000

DATA_BASE_ANTIGA = datetime(1997, 10, 7)
DATA_BASE_NOVA   = datetime(2025, 2, 22)
FATOR_REINICIO   = 1000  # valor do fator no dia 22/02/2025


def obter_data_vencimento(linha_digitavel: str):
    """
    Extrai a data de vencimento da linha digitável do boleto (47 dígitos).

    Estrutura do campo 5 (15 dígitos, índice 32-46):
      índice 32     → dígito verificador do campo 5 (ignorado)
      índice 33-36  → fator de vencimento (4 dígitos)
      índice 37-46  → valor nominal (10 dígitos)

    Regra FEBRABAN:
      - Fator 0000 → sem vencimento definido (à vista)
      - Até 21/02/2025: fator = dias desde 07/10/1997
      - A partir de 22/02/2025: fator reinicia em 1000,
        sendo fator 1000 = 22/02/2025, fator 1001 = 23/02/2025, etc.

    Para resolver a ambiguidade (mesmo fator pode ser antigo ou novo),
    calcula as duas datas possíveis e escolhe a mais próxima de hoje.

    Retorna um objeto date ou None se não for possível calcular.
    """
    try:
        codigo = linha_digitavel.replace(" ", "").replace(".", "").replace("-", "")

        if len(codigo) != 47:
            return None

        fator = int(codigo[33:37])

        if fator == 0:
            return None  # Boleto sem vencimento definido

        hoje = datetime.now()

        # Data pela base antiga (07/10/1997)
        data_antiga = DATA_BASE_ANTIGA + timedelta(days=fator)

        # Data pela nova base (22/02/2025), fator reinicia em 1000
        data_nova = DATA_BASE_NOVA + timedelta(days=fator - FATOR_REINICIO)

        # Escolhe a data mais próxima da data atual
        delta_antiga = abs((data_antiga - hoje).days)
        delta_nova   = abs((data_nova - hoje).days)

        data_vencimento = data_nova if delta_nova < delta_antiga else data_antiga

        return data_vencimento.date()

    except Exception:
        return None
