import re
from typing import Optional

def extract(pattern:str, text:str) -> Optional[str]:
    match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)

    if match:
        return match.group(1).strip()
    return None