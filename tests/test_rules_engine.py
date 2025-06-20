import pytest
import json
from mcp_server.rules_engine import loader
import os

# Test with a valid, temporary rules file
def test_load_rules_valid(mock_rules_file, monkeypatch, app): # Added app for context
    monkeypatch.setattr(loader, 'RULES_FILE', mock_rules_file)
    monkeypatch.setattr(loader, '_rules_cache', None) # Reset cache
    with app.app_context(): # Add app_context for logger access
        rules = loader.load_rules()
    assert "TEST-FORM" in rules
    assert rules["TEST-FORM"]["source_api"] == "TEST-API"

# Test with a non-existent rules file
def test_load_rules_file_not_found(tmp_path, monkeypatch, app): # Added app for context
    non_existent_file = tmp_path / "non_existent_rules.json"
    monkeypatch.setattr(loader, 'RULES_FILE', str(non_existent_file))
    monkeypatch.setattr(loader, '_rules_cache', None) # Reset cache
    with app.app_context(): # Add app_context for logger access
        rules = loader.load_rules()
    assert rules == {} # Should return empty dict

# Test with a corrupt JSON file
def test_load_rules_corrupt_json(tmp_path, monkeypatch, app): # Added app for context
    corrupt_file = tmp_path / "corrupt_rules.json"
    with open(corrupt_file, 'w') as f:
        f.write("{'invalid_json': ") # Invalid JSON
    monkeypatch.setattr(loader, 'RULES_FILE', str(corrupt_file))
    monkeypatch.setattr(loader, '_rules_cache', None) # Reset cache
    with app.app_context(): # Add app_context for logger access
        rules = loader.load_rules()
    assert rules == {} # Should return empty dict

def test_get_all_form_types(mock_rules_file, monkeypatch, app): # Added app for context
    monkeypatch.setattr(loader, 'RULES_FILE', mock_rules_file)
    monkeypatch.setattr(loader, '_rules_cache', None)
    # loader.load_rules() # Not strictly needed before get_all_form_types as it calls load_rules
    with app.app_context(): # Add app_context for logger access
        form_types = loader.get_all_form_types()
    assert "TEST-FORM" in form_types
    assert "10-K_TEST" in form_types
    assert len(form_types) == 2

def test_get_forms_by_entity_type(mock_rules_file, monkeypatch, app): # Added app for context
    monkeypatch.setattr(loader, 'RULES_FILE', mock_rules_file)
    monkeypatch.setattr(loader, '_rules_cache', None)
    # loader.load_rules() # Not strictly needed

    with app.app_context(): # Add app_context for logger access
        forms = loader.get_forms_by_entity_type("Test Entity")
        assert "TEST-FORM" in forms
        assert "10-K_TEST" in forms
        assert len(forms) == 2

        forms_us_public = loader.get_forms_by_entity_type("US Public Company")
        assert "10-K_TEST" in forms_us_public
        assert "TEST-FORM" not in forms_us_public
        assert len(forms_us_public) == 1

        forms_non_existent = loader.get_forms_by_entity_type("NonExistent Entity")
        assert len(forms_non_existent) == 0

        forms_empty_entity = loader.get_forms_by_entity_type("") # Should return all as per current logic
        assert len(forms_empty_entity) == 2


def test_get_form_details(mock_rules_file, monkeypatch, app): # Added app for context
    monkeypatch.setattr(loader, 'RULES_FILE', mock_rules_file)
    monkeypatch.setattr(loader, '_rules_cache', None)
    # loader.load_rules() # Not strictly needed

    with app.app_context(): # Add app_context for logger access
        details = loader.get_form_details("TEST-FORM")
        assert details is not None
        assert details["issuance_interval"] == "TestInterval"

        details_non_existent = loader.get_form_details("NON-EXISTENT-FORM")
        assert details_non_existent is None
