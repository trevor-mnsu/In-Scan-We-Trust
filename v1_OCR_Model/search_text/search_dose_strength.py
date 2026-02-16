import re

def search_dose_strength(text):
    """
    Finds the first dose strength in the text
    (e.g., 500 mg, 1 g, 25mcg).
    
    Returns a single string like "500 mg"
    or None if nothing is found.
    """

    dose_units = ["mg", "g", "mcg", "μg", "kg", "ml", "mL", "IU"]
    unit_pattern = "|".join(dose_units)

    pattern = rf"(\d+(?:\.\d+)?)\s*({unit_pattern})"

    match = re.search(pattern, text, flags=re.IGNORECASE)

    if match:
        number = match.group(1)
        unit = match.group(2)
        return f"{number} {unit}"

    return None
