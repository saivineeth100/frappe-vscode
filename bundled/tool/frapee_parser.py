import os
import json
import frappe


class FrappeModule:
    Name: str
    App: "FrappeApp"
    Path: str
    DocTypes: dict[str, "FrappeDocType"]

    def __init__(self, name, app, path):
        self.Name = name
        self.App = app
        self.Path = path
        self.DocTypes = {}


class FrappeApp:
    Name: str
    Version: str
    Path: str
    Modules: dict[str, FrappeModule]

    def __init__(self, name, version, path):
        self.Name = name
        self.Version = version
        self.Modules = {}
        self.Path = path


class FrappeDocType:
    Name: str
    Module: FrappeModule
    Path: str
    Fields: dict[str, "FrappeDocTypeField"]

    def __init__(self, name, module, path):
        self.Name = name
        self.Module = module
        self.Path = path
        self.Fields = {}


class FrappeDocTypeField:
    Name: str
    Type: str
    Label: str
    Required: bool
    DocType: FrappeDocType

    def __init__(self, name, type, label, required, doctype: FrappeDocType):
        self.Name = name
        self.Type = type
        self.Label = label
        self.Required = required
        self.DocType = doctype


class FrappeParser:
    FrappeApps: dict[str, FrappeApp]
    FrappeDocTypes: set[str]
    BenchLocation: str

    def __init__(self):
        self.FrappeApps = {}
        self.FrappeDocTypes = set()
        self.BenchLocation = None

    def Intialize(self, benchLocation: str):
        self.BenchLocation = benchLocation
        apps: dict = json.loads(
            frappe.read_file(
                os.path.join(self.BenchLocation, "sites", "apps.json"),
                raise_not_found=True,
            )
        )
        for app_name in apps:
            app_dict = apps.get(app_name)
            app = FrappeApp(
                app_name,
                app_dict.get("version"),
                os.path.join(self.BenchLocation, "apps", app_name),
            )
            self.FrappeApps.setdefault(app_name, app)
            self._intializeModules(app)

    def _intializeModules(self, app: FrappeApp):
        main_module_path = os.path.join(app.Path, app.Name)
        app_modules_path = os.path.join(main_module_path, "modules.txt")
        contents: str = frappe.read_file(app_modules_path)
        modules = contents.splitlines()
        for module_name in modules:

            module_path = os.path.join(main_module_path, frappe.scrub(module_name))
            module = FrappeModule(module_name, app, module_path)
            app.Modules.setdefault(module_name, module)
            self._intializeDocTypes(module)

    def _intializeDocTypes(self, module: FrappeModule):
        doc_type_parent_dir = os.path.join(module.Path, "doctype")
        dirs = get_directories_os_scandir(doc_type_parent_dir)
        for dir in dirs:
            doc_type_dir = os.path.join(doc_type_parent_dir, dir)
            doc_type_json_file = os.path.join(doc_type_dir, f"{dir}.json")
            json_text = frappe.read_file(doc_type_json_file)
            if json_text == None:
                return
            doc_type_json = json.loads(json_text)
            doc_type_fields: list = doc_type_json.get("fields", [])
            doc_type_name: str = doc_type_json.get("name")
            doc_type = FrappeDocType(doc_type_name, module, doc_type_dir)
            module.DocTypes.setdefault(doc_type_name, doc_type)
            self.FrappeDocTypes.add(doc_type_name.lower())
            for doc_type_field in doc_type_fields:
                field_type = doc_type_field.get("fieldtype")
                if field_type == "Section Break":
                    field_name = doc_type_field.get("fieldname")
                    field = FrappeDocTypeField(
                        field_name,
                        field_type,
                        doc_type_field.get("label"),
                        doc_type_field.get("reqd") == 0,
                        doc_type
                    )
                    doc_type.Fields.setdefault(field_name, field)


def get_directories_os_scandir(path):
    directories = []
    if not os.path.exists(path):
        return directories
    for entry in os.scandir(path):
        if entry.is_dir() and not entry.name.startswith("__"):
            directories.append(entry.name)
    return directories
