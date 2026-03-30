import random
from functions.gsheets import get_ids_existentes

def id_number() -> str:
    """
    Gera um ID único de 6 dígitos que não começa com 0
    e não existe ainda nas planilhas das bancas.
    """
    ids_existentes = get_ids_existentes()

    for _ in range(1000):  # Limite de tentativas para evitar loop infinito
        numero = ''.join(str(random.randint(0, 9)) for _ in range(6))
        if numero[0] != '0' and numero not in ids_existentes:
            return numero

    raise RuntimeError("Não foi possível gerar um ID único. Contate o administrador.")
