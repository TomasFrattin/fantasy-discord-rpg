def energia_max_por_afinidad(afinidad: str) -> int:
    base = 3
    if afinidad.lower() == "arcano":
        return base + 1
    return base
