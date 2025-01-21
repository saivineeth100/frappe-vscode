from frappe_vscode.frapee_parser import FrappeParser


from lsprotocol import types as lsptypes
from lsprotocol.types import CompletionItem, CompletionItemLabelDetails, Position


def GetDocTypeCompletion(name: str, frappe_parser: FrappeParser):
    doc_type = frappe_parser.FrappeDocTypes.get(name)
    app = frappe_parser.FrappeApps.get(doc_type.AppName)
    markdown_values = [
        f"**App - {doc_type.AppName}**  ",
        f"**Module -  {doc_type.ModuleName}**  ",
    ]
    if doc_type.description != None:
        markdown_values.append(f"Description - {doc_type.description}")

    mark_down = "  \n".join(markdown_values)
    item = CompletionItem(
        name,
        kind=lsptypes.CompletionItemKind.Text,
        insert_text=f'"{name}"',
        label_details=lsptypes.CompletionItemLabelDetails(
            f" Module - {doc_type.ModuleName}"
        ),
        sort_text="0",
        documentation=lsptypes.MarkupContent(
            kind=lsptypes.MarkupKind.Markdown,
            value=mark_down,
        ),
        # detail="detail",
    )
    return item
