
import * as vscode from 'vscode';
import { TreeViewHelper } from '../tree_view_helper';

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
        public readonly collapsibleState: vscode.TreeItemCollapsibleState = vscode.TreeItemCollapsibleState.Collapsed
    ) {
        super(label, collapsibleState);
        this.iconPath = new vscode.ThemeIcon("folder");
    }
}
class FolderTreeItem extends CustomTreeItem {

}
class FrappeDocTypeTree extends CustomTreeItem {
    constructor(
        public readonly label: string,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState = vscode.TreeItemCollapsibleState.Collapsed
    ) {
        super(label, collapsibleState);

    }
}
class FrappeAppDocTypeFieldTree extends CustomTreeItem {
    constructor(
        public readonly label: string,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState = vscode.TreeItemCollapsibleState.None
    ) {
        super(label, collapsibleState);
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
    getChildren(element?: CustomTreeItem | undefined): vscode.ProviderResult<CustomTreeItem[]> {

        if (element instanceof FrappeAppTree) {
            const modules: vscode.ProviderResult<CustomTreeItem[]> = [];
            // element.FrappeApp.Modules.forEach(
            //     (module, key) => {

            //         modules.push(new FrappeAppModuleTree(key, module));
            //     }
            // );
            return modules;

        }
        if (element instanceof FrappeAppModuleTree) {
            const doc_types: vscode.ProviderResult<CustomTreeItem[]> = [];
            // element.FrappeModule.DocTypes.forEach(
            //     (doc_type, key) => {

            //         doc_types.push(new FrappeDocTypeTree(key, doc_type));
            //     }
            // );
            return doc_types;
        }
        if (element instanceof FrappeDocTypeTree) {
            const doc_type_fields: vscode.ProviderResult<CustomTreeItem[]> = [];
            // element.FrappeDocType.DocTypeFields.forEach(
            //     (doc_type_field, key) => {

            //         doc_type_fields.push(new FrappeAppDocTypeFieldTree(key, doc_type_field));
            //     }
            // );
            return doc_type_fields;
        }
        if (element === null) {

            const frappApps = [];
            // for (const [app_name, app] of this.frappe_parser.FrappeApps.entries()) {
            //     frappe_apps.push(new FrappeAppTree(app_name, app, app.Version, vscode.TreeItemCollapsibleState.Collapsed));
            // }
            return frappApps;
        }
    }
    // getParent?(element: FrappeApp): vscode.ProviderResult<FrappeApp> {
    //     throw new Error('Method not implemented.');
    // }
    // resolveTreeItem?(item: vscode.TreeItem, element: FrappeApp, token: vscode.CancellationToken): vscode.ProviderResult<vscode.TreeItem> {
    //     throw new Error('Method not implemented.');
    // }


}