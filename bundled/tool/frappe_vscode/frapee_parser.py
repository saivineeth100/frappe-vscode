import os
import json

import asyncio
from collections import OrderedDict

from frappe_vscode.models.frappe_app import (
    FrappeApp,
    FrappeDocType,
    FrappeDocTypeField,
    FrappeModule,
)


import frappe


class FrappeParser:
    FrappeApps: dict[str, FrappeApp]
    FrappeDocTypes: dict[str, FrappeDocType]
    FrappeDocTypeNames: OrderedDict[str, str]
    BenchLocation: str

    def __init__(self):
        self.FrappeApps = {}
        self.FrappeDocTypeNames = OrderedDict()
        self.FrappeDocTypes = {}
        self.BenchLocation = None

    async def Intialize(self, benchLocation: str, LSP_SERVER):
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
            await self._intializeModules(app)
        self.FrappeDocTypeNames = get_ordered_dict(self.FrappeDocTypeNames)

        LSP_SERVER.send_notification("frappe/parser_intiliazed")

    async def _intializeModules(self, app: FrappeApp):
        main_module_path = os.path.join(app.Path, app.Name)
        app_modules_path = os.path.join(main_module_path, "modules.txt")
        contents: str = frappe.read_file(app_modules_path)
        modules = contents.splitlines()
        for module_name in modules:

            module_path = os.path.join(main_module_path, frappe.scrub(module_name))
            module = FrappeModule(module_name, app.Name, module_path)
            app.Modules.setdefault(module_name, module)
            await self._intializeDocTypes(module)
        app.Modules = get_ordered_dict(app.Modules)

    async def _intializeDocTypes(self, module: FrappeModule):

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
            doc_type = FrappeDocType(
                doc_type_name, module.Name, module.AppName, doc_type_dir
            )
            doc_type.description = doc_type_json.get("description")
            module.DocTypes.setdefault(doc_type_name, doc_type)
            self.FrappeDocTypes.setdefault(doc_type_name, doc_type)
            self.FrappeDocTypeNames.setdefault(
                doc_type_name.lower().strip(), doc_type_name
            )
            for doc_type_field in doc_type_fields:
                field_type = doc_type_field.get("fieldtype")
                if field_type in ["Section Break", "Tab Break", "Column Break"]:
                    continue
                field_name = doc_type_field.get("fieldname")
                field = FrappeDocTypeField(
                    field_name,
                    field_type,
                    doc_type_field.get("label"),
                    doc_type_field.get("reqd") == 0,
                )
                doc_type.Fields.setdefault(field_name, field)
            doc_type.Fields = get_ordered_dict(doc_type.Fields)
        module.DocTypes = get_ordered_dict(module.DocTypes)

    def searchDocTypeStartsWith(self, query: str, max_count=10):
        normalized_query = query.lower().strip()
        results = []
        counter = 0
        for normalized_string, original_string in self.FrappeDocTypeNames.items():
            if not normalized_string.startswith(normalized_query):
                continue
            counter += 1
            results.append(original_string)
            if not counter == max_count:
                continue
            return results
        return results


def get_directories_os_scandir(path):
    directories = []
    if not os.path.exists(path):
        return directories
    for entry in os.scandir(path):
        if entry.is_dir() and not entry.name.startswith("__"):
            directories.append(entry.name)
    return directories


def get_ordered_dict(dict: OrderedDict[str, any]):
    ordered_dict = OrderedDict(sorted(dict.items()))
    return ordered_dict
