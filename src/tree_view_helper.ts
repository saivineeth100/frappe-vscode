import { LanguageClient } from "vscode-languageclient/node";
import { FrappeApp } from "./models/FrappeApp";

export class TreeViewHelper {
    serverIntialized: boolean = false;
    onDidChangeAppTreeData?: import("vscode").EventEmitter<void | import("/home/frappe/vscode_extension/frappe-vscode/src/views/apps_provider").CustomTreeItem | import("/home/frappe/vscode_extension/frappe-vscode/src/views/apps_provider").CustomTreeItem[] | null | undefined>;
    constructor(public client: LanguageClient) {
        this.client.onNotification("frappe/parser_intiliazed", (...params: any[]) => this.handleIntializer(params));

    }
    handleIntializer(_params: any[]) {
        this.serverIntialized = true;
        this.onDidChangeAppTreeData?.fire();
    }
    async getDataFromServer() {

        const data = await this.client.sendRequest<FrappeApp[]>("frappe/get_data", { "dataType": "app" });

        return data;
    }


}