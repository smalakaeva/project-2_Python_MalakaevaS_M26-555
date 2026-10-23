"""Разбор условий where и set и списка значений для insert."""


def parse_condition(text):
    """Превращает строку "age = 28" в словарь {'age': 28}."""
    key, sep, value = text.partition("=")
    if not sep:
        raise ValueError(text)
    key = key.strip()
    if not key:
        raise ValueError(text)
    return {key: parse_value(value)}


def parse_set(text):
    """Разбирает несколько условий set, разделённых запятой."""
    result = {}
    for part in text.split(","):
        result.update(parse_condition(part))
    return result


def parse_value(text):
    """Превращает текст в значение нужного типа: str, bool или int."""
    text = text.strip()
    if len(text) >= 2 and text[0] == '"' and text[-1] == '"':
        return text[1:-1]

    if text.lower() == "true":
        return True
    if text.lower() == "false":
        return False
    try:
        return int(text)
    except ValueError:
        raise ValueError(text)


def parse_values(text):
    """Разбирает список значений в скобках: ("Sergei", 28, true)."""
    text = text.strip()
    if not text.startswith("(") or not text.endswith(")"):
        raise ValueError(text)
    return [parse_value(part) for part in text[1:-1].split(',')]
