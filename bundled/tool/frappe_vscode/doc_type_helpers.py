import ast
import re
from typing import Callable, List, Tuple, Union
from frappe_vscode.handlers.suggestion_handlers.get_list_suggestion_handler import (
    GetListSuggestionHandler,
)
from frappe_vscode.models.function_details import FunctionArgument, FunctionDetails
from frappe_vscode.handlers.base_function_suggestion_handler import (
    FunctionSuggestionsHandler,
)


from lsprotocol.types import CompletionItem, CompletionItemLabelDetails, Position
from frappe_vscode.frapee_parser import FrappeParser
from lsprotocol import types as lsptypes
from pygls.workspace.text_document import TextDocument


class FunctionCallRouter:
    def __init__(self):
        self._handlers: List[
            Tuple[Union[str, re.Pattern], FunctionSuggestionsHandler]
        ] = []

    def register_handler(
        self, pattern: Union[str, re.Pattern], handler: FunctionSuggestionsHandler
    ):
        self._handlers.append((pattern, handler))

    def get_handler(self, function_name: str):
        for pattern, handler in self._handlers:
            if isinstance(pattern, str):
                if pattern == function_name:
                    return handler
            elif isinstance(pattern, re.Pattern):
                if pattern.match(function_name):
                    return handler
        return None

    def handle(
        self, function_details: FunctionDetails, position: Position
    ) -> lsptypes.CompletionList | None:
        handler = self.get_handler(function_details.name)
        if handler == None:
            return None
        else:
            try:
                return handler.handle(function_details, position)
            except Exception as error:
                return None


class FunctionCallLocator(ast.NodeVisitor):
    args: dict[str, FunctionArgument]
    kwargs = dict[str, FunctionArgument]

    def __init__(self, code, position: Position):
        self.current_call: ast.Call | None = None
        self.position = position
        self.argument_index = 0
        self.args = {}
        self.kwargs = {}
        self.imported = {}

    def visit_ImportFrom(self, node):
        """Handle imports from"""
        for alias in node.names:
            if alias.asname:
                self.imported[alias.asname] = (
                    f"{node.module}.{alias.name}"  # from frappe import bar as baz
                )
            else:
                self.imported[alias.name] = (
                    f"{node.module}.{alias.name}"  # from frappe import bar
                )
        self.generic_visit(node)

    def visit_Import(self, node):
        for alias in node.names:
            if alias.asname:
                self.imported[alias.asname] = alias.name
            else:
                self.imported[alias.name] = alias.name
        # return super().visit_Import(node)

    def is_position_inside_call(self, node):
        """
        Checks if a given position is strictly within an ast.Call object, excluding
        positions immediately before or after the call.

        Args:
            node: The ast.Call object representing the function call.
        Returns:
            True if the position is strictly within the function call, False otherwise.
        """
        position = self.position
        if node.lineno == position.line:
            # Check if start of the call is on the same line
            # Check that the column is inside the scope, but not the left edge
            if node.col_offset < position.character:
                if node.end_lineno == position.line:
                    if node.end_col_offset > position.character:
                        return True
                elif node.end_lineno > position.line:
                    return True
        elif node.lineno < position.line < node.end_lineno:
            return True  # Check if the current line is between the start and end lines
        elif node.end_lineno == position.line:
            if position.character < node.end_col_offset:
                return True  # Check if cursor is inside the end line, but not the right edge
        return False  # return false if no conditions are true

    def visit_Call(self, node):
        if self.is_position_inside_call(node):
            self.current_call = node
            # self.generic_visit(node)
            # self.argument_index = len(self.current_call.args)
            is_index_set = False
            for i, arg in enumerate(self.current_call.args):
                index = i + 1
                if (
                    arg.lineno == self.position.line
                    and self.position.character >= arg.col_offset
                    and self.position.character <= arg.end_col_offset
                ):
                    is_index_set = True
                    self.argument_index = index
                string_value = None
                if isinstance(arg, ast.Name):
                    string_value = arg.id
                elif isinstance(arg, ast.Constant):
                    string_value = arg.value
                self.args[index] = FunctionArgument(arg, string_value)
            kwargs_count = len(self.current_call.keywords)
            if not is_index_set:
                self.argument_index = len(self.current_call.args)
                # is_index_set = kwargs_count == 0
            for i, keyword in enumerate(self.current_call.keywords):
                index = i + 1
                if (
                    self.position.character >= keyword.col_offset
                    and self.position.character <= keyword.end_col_offset
                ):
                    is_index_set = True
                    self.argument_index += index
                self.kwargs[keyword.arg] = FunctionArgument(keyword.value)
            if not is_index_set:
                self.argument_index += kwargs_count + 1


def FrappeSuggestionHelper(
    position: Position, text_document: TextDocument, frappe_parser: FrappeParser
):

    try:
        from frappe_vscode import ROUTER

        function_details = getFunctionDetails(position, text_document, True)
        return ROUTER.handle(function_details, position)
    except Exception as ex:
        pass
    return []


def getFunctionDetails(
    position: Position, text_document: TextDocument, recover=False
) -> FunctionDetails | None:
    position.line += 1
    code = text_document.source
    recovered_search_text = None
    try:
        tree = ast.parse(code)
    except Exception as err:
        if recover:
            try:
                from frappe_vscode import DOC_MANAGER

                existing_doc = DOC_MANAGER.get_doc(text_document.uri)
                if existing_doc == None:
                    return
                code = existing_doc.FullText
                tree = ast.parse(code)
                position.character -= len(existing_doc.ChangedText)
                recovered_search_text = existing_doc.ChangedText
            except Exception as nested_err:
                return None
        else:
            return None
    locator = FunctionCallLocator(code, position)
    locator.visit(tree)
    if locator.current_call == None:
        return None
    call_node = locator.current_call
    if isinstance(call_node.func, ast.Attribute):
        names = []
        value = call_node.func
        while isinstance(value, ast.Attribute):
            names.insert(0, value.attr)
            value = value.value
        names.insert(0, locator.imported.get(value.id, value.id))
        name = ".".join(names)
    elif isinstance(call_node.func, ast.Name):
        name = locator.imported.get(call_node.func.id, call_node.func.id)
    return FunctionDetails(
        name,
        call_node,
        locator.argument_index,
        locator.args,
        locator.kwargs,
        recovered_search_text,
    )
