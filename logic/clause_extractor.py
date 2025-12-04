def extract_clauses(text: str) -> dict:
    # Replaces multiple separators with a uniform one
    for sep in [".", ";", "\n"]:
        text = text.replace(sep, "|")

    parts = [p.strip() for p in text.split("|")]
    clauses = [p for p in parts if len(p) > 3]

    return {"clauses": clauses}
