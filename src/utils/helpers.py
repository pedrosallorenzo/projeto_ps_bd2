import re


# tratamento de cpf
def only_digits(s: str) -> str:
    return re.sub(r"\D+", "", s or "")
