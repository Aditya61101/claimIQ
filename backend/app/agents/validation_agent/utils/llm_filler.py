from typing import Dict, List

def llm_fill_missing_fields(
    text:str,
    missing_fields: List[str],
    document_type: str,
    claim_type: str
) -> Dict:
    """
    Asks LLM only for missing fields.
    This function should return a dict with ONLY those fields.
    """
    
    prompt = f"""
    You are extracting structured data from a medical document.
    Document type: {document_type}
    Claim type: {claim_type}

    Extract only the following fields:
    {missing_fields}

    Return valid JSON only.
    """

    # response = call_llm(prompt, text)
    # parsed = json.loads(response)
    parsed = {}

    return parsed