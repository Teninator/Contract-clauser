def categorize_clauses(clauses: list) -> dict:
    categories = {
        "payment_terms": [],
        "termination": [],
        "confidentiality": [],
        "liability": [],
        "miscellaneous": []
    }

    for c in clauses:
        lc = c.lower()

        if any(x in lc for x in ["pay", "fee", "amount", "invoice"]):
            categories["payment_terms"].append(c)
        elif any(x in lc for x in ["terminate", "termination", "end agreement"]):
            categories["termination"].append(c)
        elif any(x in lc for x in ["confidential", "non-disclosure", "nda"]):
            categories["confidentiality"].append(c)
        elif any(x in lc for x in ["liability", "indemnify", "hold harmless"]):
            categories["liability"].append(c)
        else:
            categories["miscellaneous"].append(c)

    return categories
