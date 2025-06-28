"""This module provides a service for interacting with Tree-sitter."""

from tree_sitter import Language, Parser


class TreeSitterService:
    """A service for interacting with Tree-sitter."""

    def __init__(self):
        """Initializes the TreeSitterService."""
        self.parser = Parser()

    def get_ast(self, code: str, language: str):
        """
        Gets the AST for the given code and language.

        Args:
            code: The code to parse.
            language: The language of the code.

        Returns:
            The AST for the given code and language.
        """
        # TODO: Add support for different languages.
        PY_LANGUAGE = Language("build/my-languages.so", "python")
        self.parser.set_language(PY_LANGUAGE)
        tree = self.parser.parse(bytes(code, "utf8"))
        return tree
