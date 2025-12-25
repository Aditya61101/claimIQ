def find_missing_fields(required: list[str], extracted:dict) -> list[str]:
    if not extracted:
        return required
    
    return [
        f for f in required if not extracted.get(f)
    ]