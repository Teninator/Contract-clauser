def format_section(title: str, items: list) -> str:
    # Formats a category into markdown bullet points.
    if not items:
        return f"\n### {title}:\n(No relevant clauses found)\n"
    bullets = "\n".join(f"- {i}" for i in items)
    return f"\n### {title}:\n{bullets}\n"


def build_disclosure(categorized: dict) -> str:
 
    # Builds a strict, anti-placeholder disclosure prompt.
    # Ensures the LLM only summarizes the actual contract clauses.

    sections = []
    for key, item_list in categorized.items():
        title = key.replace("_", " ").title()
        sections.append(format_section(title, item_list))

    combined = "\n".join(sections)

    return f"""
You are an AI legal assistant. 
Generate a **plain-language disclosure summary** based ONLY on the contract clauses below.

STRICT REQUIREMENTS:
- **NO placeholders** (no “Insert X”, no blanks, no templates).
- **NO formal signature sections**, NO repeated “acknowledgment” blocks.
- **NO restating the categories**—summarize what is actually there.
- Use **only information explicitly present** in the extracted clauses.
- If a category has no clauses, simply omit it from the disclosure.
- Write in **concise bullet points**, human-friendly, direct.
- Focus only on:
  - obligations
  - risks
  - rights
  - restrictions
  - costs (if any)
- This is a disclosure sheet, NOT a contract template.

Contract Clauses (organized by category):
{combined}

Now write a clear, factual disclosure sheet summarizing these clauses in bullet form.
Do NOT add anything that is not clearly supported by the text.
"""
