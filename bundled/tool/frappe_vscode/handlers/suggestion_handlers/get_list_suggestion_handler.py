from frappe_vscode.frapee_parser import FrappeParser


from frappe_vscode.models.function_details import FunctionDetails
from frappe_vscode.handlers.base_function_suggestion_handler import (
    FunctionSuggestionsHandler,
)
from frappe_vscode.utils import GetDocTypeCompletion
from lsprotocol import types as lsptypes


class GetListSuggestionHandler(FunctionSuggestionsHandler):
    def __init__(self, frappe_parser: FrappeParser):
        super().__init__(frappe_parser)

    def handle(self, function_details: FunctionDetails):
        frappe_parser = self.frappe_parser
        selected_index = function_details.current_argument_index
        args = function_details.args
        if selected_index == 1:
            matched_doctypes = frappe_parser.searchDocTypeStartsWith(
                args.get(selected_index)
            )
            CompletionItems = [
                GetDocTypeCompletion(i, frappe_parser) for i in matched_doctypes
            ]
            is_complete = len(matched_doctypes) < 10
            return lsptypes.CompletionList(not is_complete, CompletionItems)
        else:
            kwarg_index = 2
            for kwarg_key in function_details.kwargs:
                val = function_details.kwargs[kwarg_key]
                kwarg_index += 1
                pass
            pass
        return super().handle()
