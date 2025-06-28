from mcp_server.utils.unicode_ast import (
    UNICODE_AST_SYMBOLS,
    code_to_unicode_ast,
    unicode_ast_to_code,
)


def test_unicode_ast_symbols_defined():
    assert isinstance(UNICODE_AST_SYMBOLS, dict)
    assert len(UNICODE_AST_SYMBOLS) > 0
    assert "function" in UNICODE_AST_SYMBOLS
    assert "variable" in UNICODE_AST_SYMBOLS


def test_code_to_unicode_ast_function():
    code = "def my_func():\n    pass"
    unicode_ast = code_to_unicode_ast(code)
    assert unicode_ast.startswith(UNICODE_AST_SYMBOLS["function"])
    assert UNICODE_AST_SYMBOLS["block"] in unicode_ast


def test_code_to_unicode_ast_variable():
    code = "my_var = 10"
    unicode_ast = code_to_unicode_ast(code)
    assert unicode_ast.startswith(UNICODE_AST_SYMBOLS["variable"])
    assert UNICODE_AST_SYMBOLS["assignment"] in unicode_ast
    assert UNICODE_AST_SYMBOLS["literal"] in unicode_ast


def test_unicode_ast_to_code_function():
    unicode_ast = f"{UNICODE_AST_SYMBOLS['function']} func_name {UNICODE_AST_SYMBOLS['block']}"
    code = unicode_ast_to_code(unicode_ast)
    assert code == "def func_name():\n    pass"


def test_unicode_ast_to_code_variable():
    unicode_ast = f"{UNICODE_AST_SYMBOLS['variable']} var_name {UNICODE_AST_SYMBOLS['assignment']} {UNICODE_AST_SYMBOLS['literal']} value"
    code = unicode_ast_to_code(unicode_ast)
    assert code == "var_name = value"
