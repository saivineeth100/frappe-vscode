# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from frappe_vscode.doc_manager import DocManager
from frappe_vscode.doc_type_helpers import FunctionCallRouter
from frappe_vscode.frapee_parser import FrappeParser
import re
from frappe_vscode.handlers.suggestion_handlers.get_list_suggestion_handler import (
    GetListSuggestionHandler,
)

FRAPPE_PARSER = FrappeParser()
ROUTER = FunctionCallRouter()
DOC_MANAGER = DocManager()

ROUTER.register_route(
    re.compile(r"frappe(?:\.db)?\.get_list"), GetListSuggestionHandler(FRAPPE_PARSER)
)
