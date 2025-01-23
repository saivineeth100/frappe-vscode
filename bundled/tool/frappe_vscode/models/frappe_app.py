from collections import OrderedDict


class FrappeApp:
    Name: str
    Version: str
    Path: str
    Modules: OrderedDict[str, "FrappeModule"]

    def __init__(self, name, version, path):
        self.Name = name
        self.Version = version
        self.Modules = OrderedDict()
        self.Path = path


class FrappeModule:
    Name: str
    AppName: str
    Path: str
    DocTypes: OrderedDict[str, "FrappeDocType"]
    Reports: OrderedDict[str, "FrappeReport"]

    def __init__(self, name, app_name, path):
        self.Name = name
        self.AppName = app_name
        self.Path = path
        self.DocTypes = OrderedDict()
        self.Reports = OrderedDict()


class FrappeReport:
    Name: str
    ModuleName: str
    Path: str
    IsStandard: bool = False
    ReportType: str
    AppName: str

    def __init__(self, name, report_tpe, module_name, app_name, path):
        self.Name = name
        self.ReportType = report_tpe
        self.ModuleName = module_name
        self.AppName = app_name
        self.Path = path


class FrappeDocType:
    Name: str
    ModuleName: str
    Path: str
    Fields: OrderedDict[str, "FrappeDocTypeField"]
    description: str | None

    def __init__(self, name, module_name, app_name, path):
        self.Name = name
        self.ModuleName = module_name
        self.AppName = app_name
        self.Path = path
        self.Fields = OrderedDict()
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
