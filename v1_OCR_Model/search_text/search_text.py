#import all search functions
from search_text.search_dose_strength import search_dose_strength
from search_text.search_brand import search_brand_name
from search_text.search_medication_name import search_medicine_name_first_line

#apply all search functions to the text
def search_text(text):
    """
    Runs extraction functions and replaces missing values
    with 'Not Found'.
    """

    dose_strength = search_dose_strength(text)
    brand_name = search_brand_name(text)
    medicine_name = search_medicine_name_first_line(text)

    #assign key to value pair; if not found set "Not Found"
    results = {
        "medication_name": medicine_name if medicine_name else "Not Found",
        "brand_name": brand_name if brand_name else "Not Found",
        "dose_strength": dose_strength if dose_strength else "Not Found"
    }

    return results
