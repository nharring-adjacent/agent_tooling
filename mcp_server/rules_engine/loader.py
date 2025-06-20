import json
import os
from flask import current_app # Import current_app for logging

RULES_FILE = os.path.join(os.path.dirname(__file__), 'rules.json')

_rules_cache = None

def load_rules():
    """Loads the rules from the JSON file."""
    global _rules_cache
    if _rules_cache is None: # Only load if not already cached
        try:
            with open(RULES_FILE, 'r') as f:
                _rules_cache = json.load(f)
            if hasattr(current_app, 'logger'):
                current_app.logger.info(f"Successfully loaded rules from {RULES_FILE}")
            else: # Fallback for when logger might not be available (e.g. testing outside app context)
                print(f"INFO: Successfully loaded rules from {RULES_FILE}")
        except FileNotFoundError:
            if hasattr(current_app, 'logger'):
                current_app.logger.error(f"Rules file not found at {RULES_FILE}")
            else:
                print(f"ERROR: Rules file not found at {RULES_FILE}")
            _rules_cache = {} # Ensure cache is an empty dict on error
        except json.JSONDecodeError as e:
            if hasattr(current_app, 'logger'):
                current_app.logger.error(f"Could not decode JSON from {RULES_FILE}: {e}")
            else:
                print(f"ERROR: Could not decode JSON from {RULES_FILE}: {e}")
            _rules_cache = {} # Ensure cache is an empty dict on error
        except Exception as e: # Catch any other unexpected errors during loading
            if hasattr(current_app, 'logger'):
                current_app.logger.error(f"An unexpected error occurred while loading rules from {RULES_FILE}: {e}", exc_info=True)
            else:
                print(f"ERROR: An unexpected error occurred while loading rules from {RULES_FILE}: {e}")
            _rules_cache = {}
    return _rules_cache

def get_all_form_types():
    """Returns a list of all available form types."""
    rules = load_rules()
    return list(rules.keys())

def get_forms_by_entity_type(entity_type: str):
    """
    Filters forms based on the relevant_entity_types.
    Returns a list of form types applicable to the given entity_type.
    """
    rules = load_rules()
    applicable_forms = []
    # It might be better to raise an error or return empty if entity_type is not provided.
    # Current behavior: if not entity_type, returns all forms.
    if not entity_type:
        if hasattr(current_app, 'logger'):
            current_app.logger.warning("get_forms_by_entity_type called with no entity_type. Returning all forms.")
        else:
            print("WARN: get_forms_by_entity_type called with no entity_type. Returning all forms.")
        return get_all_form_types()

    for form_type, properties in rules.items():
        if entity_type in properties.get('relevant_entity_types', []):
            applicable_forms.append(form_type)
    return applicable_forms

def get_form_details(form_type: str):
    """
    Returns the details for a specific form_type.
    """
    rules = load_rules()
    details = rules.get(form_type)
    if not details and hasattr(current_app, 'logger'):
        current_app.logger.warning(f"Details not found for form_type: {form_type}")
    return details

if __name__ == '__main__':
    # This example usage will use print since it's outside Flask app context
    print("Loading rules (standalone execution)...")
    all_rules = load_rules() # Will use print for logging here
    if all_rules:
        print(f"Loaded {len(all_rules)} rules.")
        print("\nAll form types:", get_all_form_types())
        us_public_forms = get_forms_by_entity_type("US Public Company")
        print(f"\nForms for 'US Public Company': {us_public_forms}")
        pre_ipo_forms = get_forms_by_entity_type("Pre-IPO Company")
        print(f"Forms for 'Pre-IPO Company': {pre_ipo_forms}")
        print("\nDetails for 10-K:", get_form_details("10-K"))
        print("Details for NonExistentForm:", get_form_details("NonExistentForm"))
    else:
        print("No rules were loaded.")
