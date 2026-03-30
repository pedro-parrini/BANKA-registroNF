def obter_valor_boleto(linha_digitavel: str):
    """
    Extrai o valor do boleto a partir da linha digitável (47 dígitos).

    Estrutura da linha digitável (posições base-1):
      Posições 38-47 → valor nominal do título (10 dígitos, sem vírgula,
                        dois últimos são centavos)

    Valor "0000000000" → boleto sem valor definido (ex: carnês com valor variável).

    Retorna float ou None se não for possível extrair.
    """
    try:
        # Limpar a entrada
        codigo = linha_digitavel.replace(" ", "").replace(".", "").replace("-", "")

        # Linha digitável deve ter 47 dígitos
        if len(codigo) != 47:
            return None

        # Posições 38 a 47 (índice 0: 37 a 46)
        valor_str = codigo[37:47]

        # Valor zerado = sem valor fixo
        if int(valor_str) == 0:
            return None

        return int(valor_str) / 100

    except Exception:
        return None
