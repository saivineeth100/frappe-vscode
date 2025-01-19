import { LanguageClient } from "vscode-languageclient/node";

export class TreeViewHelper {
    onDidChangeAppTreeData?: import("vscode").EventEmitter<void | import("/home/frappe/vscode_extension/frappe-vscode/src/views/apps_provider").CustomTreeItem | import("/home/frappe/vscode_extension/frappe-vscode/src/views/apps_provider").CustomTreeItem[] | null | undefined>;
    constructor(client: LanguageClient) {

    }



}