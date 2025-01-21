class FrappeApp:
    Name: str
    Version: str
    Path: str
    Modules: dict[str, "FrappeModule"]

    def __init__(self, name, version, path):
        self.Name = name
        self.Version = version
        self.Modules = {}
        self.Path = path


class FrappeModule:
    Name: str
    AppName: str
    Path: str
    DocTypes: dict[str, "FrappeDocType"]

    def __init__(self, name, app_name, path):
        self.Name = name
        self.AppName = app_name
        self.Path = path
        self.DocTypes = {}


class FrappeDocType:
    Name: str
    ModuleName: str
    Path: str
    Fields: dict[str, "FrappeDocTypeField"]
    description: str | None

    def __init__(self, name, module_name, app_name, path):
        self.Name = name
        self.ModuleName = module_name
        self.AppName = app_name
        self.Path = path
        self.Fields = {}
        self.description = None


class FrappeDocTypeField:
    Name: str
    Type: str
    Label: str
    Required: bool

    def __init__(self, name, type, label, required):
        self.Name = name
        self.Type = type
        self.Label = label
        self.Required = required
