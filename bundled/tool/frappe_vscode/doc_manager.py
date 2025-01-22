from lsprotocol.types import Position


class DocChanges:
    ChangedText: str
    StartPosition: Position
    FullText: str

    def __init__(
        self,
        changed_text: str,
        start_position: Position,
        full_text,
    ):
        self.ChangedText = changed_text
        self.StartPosition = start_position
        self.FullText = full_text


class DocManager:
    Docs = {}

    def add_to_docs(self, uri, changes: DocChanges):
        self.Docs[uri] = changes

    def get_doc(self, uri) -> DocChanges:
        return self.Docs.get(uri, None)
