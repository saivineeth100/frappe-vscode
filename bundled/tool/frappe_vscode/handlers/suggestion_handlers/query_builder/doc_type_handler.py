import ast
from frappe_vscode.utils import get_doc_type_suggestions
from frappe_vscode.handlers.base_function_suggestion_handler import (
    FunctionSuggestionsHandler,
)

from frappe_vscode.models.function_details import FunctionDetails
from lsprotocol import types as lsptypes


class QueryBuilderDocTypeSuggestionHandler(FunctionSuggestionsHandler):

    def handle(self, function_details: FunctionDetails, position: lsptypes.Position):
        self.position = position
        frappe_parser = self.frappe_parser
        selected_index = function_details.current_argument_index
        args = function_details.args
        if selected_index == 1:
            current_arg = args.get(selected_index)
            within_string = isinstance(current_arg.arg_value, ast.Constant)
            query_string = current_arg.string_value
            completion_list = get_doc_type_suggestions(
                frappe_parser, query_string, within_string
            )
            return completion_list
