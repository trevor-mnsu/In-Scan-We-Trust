'''
Names tend to be the first few words on the page.
Names tend to be bigger and bold text on blister sheets
IDK what else... look into it :)
'''

import re

def search_medicine_name_first_line(text):
    """
    Attempts to detect a medicine name on the first non-empty line.

    Heuristic:
    - Looks at first non-empty line
    - Allows uppercase words
    - Allows numbers
    - Allows common pharma patterns (HCL, XR, mg)
    - Avoids lines that are mostly dosage-only

    Returns:
        str: detected medicine name
        None: if no valid name found
    """

    if not text:
        return None

    lines = [line.strip() for line in text.split("\n") if line.strip()]
    if not lines:
        return None

    first_line = lines[0]

    # Reject if line is mostly dosage (e.g., "500 mg")
    if re.match(r'^\d+\s?(mg|g|ml|mcg)$', first_line, re.IGNORECASE):
        return None

    words = first_line.split()

    # Medicine names usually 1–5 words
    if len(words) > 6:
        return None

    valid_words = 0

    for word in words:
        if re.match(r'^[A-Za-z0-9\-]+$', word):
            valid_words += 1

    # Require at least one alphabetic word
    has_alpha = any(re.search(r'[A-Za-z]', w) for w in words)

    if valid_words >= 1 and has_alpha:
        return first_line

    return None
