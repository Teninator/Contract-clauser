from logic.clause_extractor import extract_clauses
from logic.clause_finder import categorize_clauses
from logic.disclosure_generator import build_disclosure
from llm.llm_client import run_llm

def process_document(text: str) -> str:
    """
    Full pipeline:
    raw text → extracted clauses → categorized → formatted disclosure → LLM → output
    """
    # 1. Extracts raw clauses
    clauses = extract_clauses(text)

    # 2. Categorizes clauses
    categorized = categorize_clauses(clauses)

    # 3. Builds prompt
    prompt = build_disclosure(categorized)

    # 4. Sends to LLM
    result = run_llm(prompt)

    return result
