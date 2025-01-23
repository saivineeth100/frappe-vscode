
import * as vscode from 'vscode';
import { TreeViewHelper } from '../tree_view_helper';
import { FrappeApp, FrappeModule, FrappeDocType, FrappeDocTypeField, FrappeReport } from '../models/FrappeApp';

export class CustomTreeItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState
    ) {
        super(label, collapsibleState);
        this.tooltip = `${this.label}`;
        // this.iconPath
    }
    // iconPath = {
    //     light: path.join(__filename, '..', '..', 'resources', 'light', 'dependency.svg'),
    //     dark: path.join(__filename, '..', '..', 'resources', 'dark', 'dependency.svg')
    // };
}
class FrappeAppTree extends CustomTreeItem {
    constructor(
        public readonly label: string,
        public readonly app: FrappeApp,
        private version?: string,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState = vscode.TreeItemCollapsibleState.Collapsed
    ) {
        super(label, collapsibleState);
        this.tooltip = `${this.label}-${this.version}`;
        this.description = this.version;
        // this.iconPath
    }
}
class FrappeAppModuleTree extends CustomTreeItem {
    constructor(
        public readonly label: string,
        public readonly module: FrappeModule,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState = vscode.TreeItemCollapsibleState.Collapsed
    ) {
        super(label, collapsibleState);
        this.iconPath = new vscode.ThemeIcon("folder");
    }
}
class FolderTreeItem extends CustomTreeItem {
    constructor(public readonly label: string,
        public readonly module: FrappeModule,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState = vscode.TreeItemCollapsibleState.Collapsed) {
        super(label, collapsibleState);
        this.iconPath = new vscode.ThemeIcon("folder");
    }

}
class FrappeReportTree extends CustomTreeItem {
    constructor(
        public readonly label: string,
        public readonly frappeReport: FrappeReport,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState = vscode.TreeItemCollapsibleState.None
    ) {
        super(label, collapsibleState);

    }
}
class FrappeDocTypeTree extends CustomTreeItem {
    constructor(
        public readonly label: string,
        public readonly docType: FrappeDocType,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState = vscode.TreeItemCollapsibleState.Collapsed
    ) {
        super(label, collapsibleState);

    }
}
class FrappeAppDocTypeFieldTree extends CustomTreeItem {
    constructor(
        public readonly docTypeField: FrappeDocTypeField,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState = vscode.TreeItemCollapsibleState.None
    ) {
        super(`${docTypeField.Name}(${docTypeField.Label})`, collapsibleState);
        this.iconPath = new vscode.ThemeIcon("variable");
        // this.tooltip = `label - ${FrappeDocTypeField.Label},Field Type - ${FrappeDocTypeField.FieldType}`
    }
}
export class FrappeTreeViewProvider implements vscode.TreeDataProvider<CustomTreeItem> {
    treeViewHelper: TreeViewHelper;


    constructor(treeViewHelper: TreeViewHelper) {
        this.treeViewHelper = treeViewHelper;
        this.treeViewHelper.onDidChangeAppTreeData = new vscode.EventEmitter<void | CustomTreeItem | CustomTreeItem[] | null | undefined>();
        this.onDidChangeTreeData = this.treeViewHelper.onDidChangeAppTreeData.event;

    }

    onDidChangeTreeData?: vscode.Event<void | CustomTreeItem | CustomTreeItem[] | null | undefined> | undefined;
    getTreeItem(element: CustomTreeItem): vscode.TreeItem | Thenable<vscode.TreeItem> {
        return element;
    }
    async getChildren(element?: CustomTreeItem | undefined): Promise<CustomTreeItem[] | undefined> {
        if (!this.treeViewHelper.serverIntialized) {
            return [];
        }
        if (element instanceof FrappeAppTree) {
            const modules: FrappeAppModuleTree[] = [];
            for (const moduleKey in element.app.Modules) {
                const module = element.app.Modules[moduleKey];
                modules.push(new FrappeAppModuleTree(moduleKey, module));
            }
            return modules;

        }
        if (element instanceof FrappeAppModuleTree) {


            return [
                new FolderTreeItem("DocTypes", element.module),
                new FolderTreeItem("Reports", element.module),
            ];
        }
        if (element instanceof FolderTreeItem) {
            if (element.label === "DocTypes") {
                const docTypes: FrappeDocTypeTree[] = [];
                for (const docKey in element.module.DocTypes) {
                    const docType = element.module.DocTypes[docKey];
                    docTypes.push(new FrappeDocTypeTree(docKey, docType));
                }
                return docTypes;
            }
            if (element.label === "Reports") {
                const reports: FrappeReportTree[] = [];
                for (const reportName in element.module.Reports) {
                    const report = element.module.DocTypes[reportName];
                    reports.push(new FrappeReportTree(reportName, report));
                }
                return reports;
            }
        }
        if (element instanceof FrappeDocTypeTree) {
            const docTypeFields: FrappeAppDocTypeFieldTree[] = [];
            for (const fieldKey in element.docType.Fields) {
                const docTypeField = element.docType.Fields[fieldKey];
                docTypeFields.push(new FrappeAppDocTypeFieldTree(docTypeField));
            }
            return docTypeFields;
        }
        if (element === undefined || element === null) {

            const frappApps: FrappeAppTree[] = [];
            const apps = await this.treeViewHelper.getDataFromServer();
            for (const app of apps) {
                frappApps.push(new FrappeAppTree(app.Name, app, app.Version, vscode.TreeItemCollapsibleState.Collapsed));
            }
            return frappApps;
        }
        return undefined;
    }
    // getParent?(element: FrappeApp): vscode.ProviderResult<FrappeApp> {
    //     throw new Error('Method not implemented.');
    // }
    // resolveTreeItem?(item: vscode.TreeItem, element: FrappeApp, token: vscode.CancellationToken): vscode.ProviderResult<vscode.TreeItem> {
    //     throw new Error('Method not implemented.');
    // }


}