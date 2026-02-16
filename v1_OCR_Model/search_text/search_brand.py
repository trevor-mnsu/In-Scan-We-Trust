import re

def search_brand_name(text):
    """
    Looks for a word followed by a copyright or trademark symbol:
    ©  ®  ™

    Returns the brand name without the symbol.
    Returns None if nothing is found.
    """

    # Pattern explanation:
    # ([A-Za-z0-9&\-]+)  -> captures the brand name
    # \s*                -> optional space
    # [©®™]              -> one of the symbols

    pattern = r"([A-Za-z0-9&\-]+)\s*[©®™]"

    match = re.search(pattern, text)

    if match:
        brand_name = match.group(1)
        return brand_name

    return None
