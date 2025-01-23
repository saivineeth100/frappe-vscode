/* eslint-disable @typescript-eslint/naming-convention */
export class FrappeModule {
    Name: string;
    AppName: string;
    Path: string;
    DocTypes: { [key: string]: FrappeDocType };
    Reports: { [key: string]: FrappeReport };

    constructor(name: string, appName: string, path: string) {
        this.Name = name;
        this.AppName = appName;
        this.Path = path;
        this.DocTypes = {};
        this.Reports = {};
    }
}
export class FrappeReport {
    Name: string;
    ModuleName: string;
    Path: string;

    constructor(name: string, moduleName: string, path: string) {
        this.Name = name;
        this.ModuleName = moduleName;
        this.Path = path;
    }
}
export class FrappeApp {
    Name: string;
    Version: string;
    Path: string;
    Modules: { [key: string]: FrappeModule };

    constructor(name: string, version: string, path: string) {
        this.Name = name;
        this.Version = version;
        this.Path = path;
        this.Modules = {};
    }
}

export class FrappeDocType {
    Name: string;
    ModuleName: string;
    Path: string;
    Fields: { [key: string]: FrappeDocTypeField };

    constructor(name: string, moduleName: string, path: string) {
        this.Name = name;
        this.ModuleName = moduleName;
        this.Path = path;
        this.Fields = {};
    }
}

export class FrappeDocTypeField {
    Name: string;
    Type: string;
    Label: string;
    Required: boolean;

    constructor(name: string, type: string, label: string, required: boolean) {
        this.Name = name;
        this.Type = type;
        this.Label = label;
        this.Required = required;
    }
}

