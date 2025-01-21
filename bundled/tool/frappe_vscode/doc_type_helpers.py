import ast
import re
from typing import Callable, List, Tuple, Union
from frappe_vscode.handlers.suggestion_handlers.get_list_suggestion_handler import (
    GetListSuggestionHandler,
)
from frappe_vscode.models.function_details import FunctionDetails
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

    def register_route(
        self, pattern: Union[str, re.Pattern], handler: FunctionSuggestionsHandler
    ):
        self._handlers.append((pattern, handler))

    def get_route(self, function_name: str):
        for pattern, handler in self._handlers:
            if isinstance(pattern, str):
                if pattern == function_name:
                    return handler
            elif isinstance(pattern, re.Pattern):
                if pattern.match(function_name):
                    return handler
        return None

    def handle(
        self, function_details: FunctionDetails
    ) -> lsptypes.CompletionList | None:
        handler = self.get_route(function_details.name)
        if handler == None:
            return None
        else:
            try:
                return handler.handle(function_details)
            except:
                return None


class FunctionCallLocator(ast.NodeVisitor):
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

    def visit_Call(self, node):
        if node.lineno <= self.position.line and self.position.line <= node.end_lineno:
            self.current_call = node
            # self.generic_visit(node)
            self.argument_index = len(self.current_call.args)
            for i, arg in enumerate(self.current_call.args):
                index = i + 1
                if (
                    arg.lineno == self.position.line
                    and self.position.character >= arg.col_offset
                    and self.position.character <= arg.end_col_offset
                ):
                    self.argument_index = index

                if isinstance(arg, ast.Name):
                    self.args.setdefault(index, arg.id)
                elif isinstance(arg, ast.Constant):
                    self.args.setdefault(index, arg.value)
                else:
                    self.args.setdefault(index, arg)

            for i, keyword in enumerate(self.current_call.keywords):
                index = i + 1
                if (
                    self.position.character >= keyword.col_offset
                    and self.position.character <= keyword.end_col_offset
                ):
                    self.argument_index += index
                self.kwargs[keyword.arg] = keyword.value


def FrappeSuggestionHelper(
    position: Position, text_document: TextDocument, frappe_parser: FrappeParser
):
    position.line += 1
    try:
        from frappe_vscode import ROUTER

        function_details = getFunctionDetails(position, text_document)
        return ROUTER.handle(function_details)
    except:
        pass
    return []


def getFunctionDetails(
    position: Position, text_document: TextDocument
) -> FunctionDetails | None:

    code = text_document.source
    try:
        tree = ast.parse(code)
    except:
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
        name, call_node, locator.argument_index, locator.args, locator.kwargs
    )
