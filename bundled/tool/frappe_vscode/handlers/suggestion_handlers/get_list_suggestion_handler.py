from frappe_vscode.frapee_parser import FrappeParser


from frappe_vscode.models.function_details import FunctionDetails
from frappe_vscode.handlers.base_function_suggestion_handler import (
    FunctionSuggestionsHandler,
)
from frappe_vscode.utils import GetDocTypeCompletion, get_default_doc_fields
from lsprotocol import types as lsptypes

import ast


class GetListSuggestionHandler(FunctionSuggestionsHandler):
    def __init__(self, frappe_parser: FrappeParser):
        super().__init__(frappe_parser)

    def handle(self, function_details: FunctionDetails, position: lsptypes.Position):
        self.position = position
        frappe_parser = self.frappe_parser
        selected_index = function_details.current_argument_index
        args = function_details.args
        if selected_index == 1:
            current_arg = args.get(selected_index)
            matched_doctypes = frappe_parser.searchDocTypeStartsWith(
                current_arg.string_value
            )
            within_string = isinstance(current_arg.arg_value, ast.Constant)
            CompletionItems = [
                GetDocTypeCompletion(i, frappe_parser, within_string)
                for i in matched_doctypes
            ]
            is_complete = len(matched_doctypes) < 10
            return lsptypes.CompletionList(not is_complete, CompletionItems)
        else:

            """
            in this method after first args (doc_type) we can pass any args or kwargs,
            docs suggest kwargs only but since we can pass args, Checking them also
            """
            if len(args) > 1:
                arg = args[selected_index]
                arg_value = arg.string_value
                """ 
                is arg_value is string then user trying to type keyword for kwargs
                So will suggest availaible keywords
                """
                if isinstance(arg_value, str):
                    k_suggestions = [i for i in KeywordArgs if i.startswith(arg_value)]
                    return lsptypes.CompletionList(
                        True,
                        [self.get_kwarg_completion_item(i) for i in k_suggestions],
                    )
                pass
            else:
                kwarg_index = 2
                existing_kwargs = []
                for kwarg_key in function_details.kwargs:
                    existing_kwargs.append(kwarg_key)
                    if kwarg_index == selected_index:
                        val = function_details.kwargs[kwarg_key].arg_value
                        kwarg = KeywordArgs.get(kwarg_key, None)
                        if kwarg == None:
                            return
                        handler = kwarg.get("handler", None)
                        if handler == None:
                            return
                        return handler(val, function_details, position)

                    kwarg_index += 1
                    pass
                if kwarg_index == selected_index:
                    k_suggestions = [
                        i
                        for i in KeywordArgs
                        if i not in existing_kwargs
                        and (
                            function_details.RecoveredSearchText == None
                            or i.startswith(function_details.RecoveredSearchText)
                        )
                    ]
                    return lsptypes.CompletionList(
                        True,
                        [self.get_kwarg_completion_item(i) for i in k_suggestions],
                    )
        return super().handle()

    def get_kwarg_completion_item(self, key):
        kw_arg: dict = KeywordArgs[key]
        completion_suffix = kw_arg.get("completion_suffix", None)
        insert_text = (
            f"{key}" if completion_suffix is None else f"{key}={completion_suffix}"
        )
        is_suffix_template = kw_arg.get("is_suffix_template", False)

        return lsptypes.CompletionItem(
            key,
            detail=f"[frappe-vscode] keyword Arg",
            insert_text=insert_text,
            insert_text_format=(
                lsptypes.InsertTextFormat.Snippet
                if is_suffix_template
                else lsptypes.InsertTextFormat.PlainText
            ),
            sort_text="0",
        )


def fields_arg_handler(
    val, function_details: FunctionDetails, position: lsptypes.Position
):
    if not isinstance(val, ast.List):
        return

    doc_type_name = function_details.args.get(1).string_value
    if doc_type_name == None:
        return
    from frappe_vscode import FRAPPE_PARSER

    doc_type = FRAPPE_PARSER.FrappeDocTypes.get(doc_type_name)
    existing_fields = []
    suggested_fields = []
    search_query = ""
    within_string = False
    for index, item in enumerate(val.elts):
        if (
            item.lineno == position.line
            and item.col_offset <= position.character
            and item.end_col_offset >= position.character
        ):
            if isinstance(item, ast.Name):
                search_query = item.id
            elif isinstance(item, ast.Constant):
                search_query = item.value
                within_string = True

        if isinstance(item, ast.Constant):
            existing_fields.append(item.value)
    all_field_names = list(doc_type.Fields.keys()) + get_default_doc_fields()
    if len(existing_fields) > 0:
        for key in all_field_names:
            if key in existing_fields:
                continue
            suggested_fields.append(key)
    else:
        suggested_fields = all_field_names
    completion_items = []
    counter = 0
    for field_name in suggested_fields:
        field = doc_type.Fields.get(field_name, None)
        if not (
            field_name.startswith(search_query)
            or search_query in field_name
            or (
                field is not None
                and (
                    search_query in field.Label or field.Label.startswith(search_query)
                )
            )
        ):
            continue
        counter += 1

        if field == None:
            completion_items.append(
                lsptypes.CompletionItem(
                    field_name,
                    kind=lsptypes.CompletionItemKind.Text,
                    insert_text=field_name if within_string else f'"{field_name}"',
                    sort_text="0",
                )
            )
            continue
        if counter == 10:
            return lsptypes.CompletionList(True, completion_items)
        completion_items.append(
            lsptypes.CompletionItem(
                field.Label,
                kind=lsptypes.CompletionItemKind.Text,
                insert_text=field_name if within_string else f'"{field.Name}"',
                sort_text="0",
            )
        )
    return lsptypes.CompletionList(False, completion_items)


KeywordArgs = {
    "fields": {
        "completion_suffix": "[$0]",
        "handler": fields_arg_handler,
        "is_suffix_template": True,
    },
    "filters": {"completion_suffix": "[$0]"},
    "or_filters": {},
    "docstatus": {},
    "group_by": {},
    "order_by": {},
    "limit_start": {},
    "limit_page_length": {},
    "as_list": {},
    "with_childnames": {},
    "debug": {},
    "ignore_permissions": {},
    "user": {},
    "with_comment_count": {},
    "join": {},
    "distinct": {},
    "start": {},
    "page_length": {},
    "limit": {},
    "ignore_ifnull": {},
    "save_user_settings": {},
    "save_user_settings_fields": {},
    "update": {},
    "add_total_row": {},
    "user_settings": {},
    "reference_doctype": {},
    "run": {},
    "strict": {},
    "pluck": {},
    "ignore_ddl": {},
    "parent_doctype": {},
}
