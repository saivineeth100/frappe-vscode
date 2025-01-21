// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

import * as vscode from 'vscode';
import { LanguageClient, ProtocolRequestType0 } from 'vscode-languageclient/node';
import { registerLogger, traceError, traceLog, traceVerbose } from './common/log/logging';
import {
    checkVersion,
    getInterpreterDetails,
    initializePython,
    onDidChangePythonInterpreter,
    resolveInterpreter,
} from './common/python';
import { restartServer } from './common/server';
import { checkIfConfigurationChanged, getInterpreterFromSetting } from './common/settings';
import { loadServerDefaults } from './common/setup';
import { getLSClientTraceLevel } from './common/utilities';
import { createOutputChannel, onDidChangeConfiguration, registerCommand } from './common/vscodeapi';
import { runBenchFindCommand } from './commands/bench_commands';
import { TreeViewHelper } from './tree_view_helper';
import { FrappeTreeViewProvider } from './views/apps_provider';

let lsClient: LanguageClient | undefined;
let treeViewHelper: TreeViewHelper | undefined;
export async function activate(context: vscode.ExtensionContext): Promise<void> {
    // This is required to get server name and module. This should be
    // the first thing that we do in this extension.
    const serverInfo = loadServerDefaults();
    const serverName = serverInfo.name;
    const serverId = serverInfo.module;

    // Setup logging
    const outputChannel = createOutputChannel(serverName);
    context.subscriptions.push(outputChannel, registerLogger(outputChannel));

    const changeLogLevel = async (c: vscode.LogLevel, g: vscode.LogLevel) => {
        const level = getLSClientTraceLevel(c, g);
        await lsClient?.setTrace(level);
    };

    context.subscriptions.push(
        outputChannel.onDidChangeLogLevel(async (e) => {
            await changeLogLevel(e, vscode.env.logLevel);
        }),
        vscode.env.onDidChangeLogLevel(async (e) => {
            await changeLogLevel(outputChannel.logLevel, e);
        }),
    );

    // Log Server information
    traceLog(`Name: ${serverInfo.name}`);
    traceLog(`Module: ${serverInfo.module}`);
    traceVerbose(`Full Server Info: ${JSON.stringify(serverInfo)}`);
    let benchLocation: string | undefined = undefined;
    const runServer = async () => {
        const interpreter = getInterpreterFromSetting(serverId);
        try {
            benchLocation = runBenchFindCommand();
        } catch (error) {

        }
        if (benchLocation === undefined) {
            return;
        }
        if (interpreter && interpreter.length > 0) {
            if (checkVersion(await resolveInterpreter(interpreter))) {
                traceVerbose(`Using interpreter from ${serverInfo.module}.interpreter: ${interpreter.join(' ')}`);
                lsClient = await restartServer(serverId, serverName, outputChannel, benchLocation, lsClient);
                treeViewHelper = new TreeViewHelper(lsClient!);
                const appTreeViewProvider = new FrappeTreeViewProvider(treeViewHelper);
                vscode.window.createTreeView('frappe_apps', {
                    treeDataProvider: appTreeViewProvider
                });
            }
            return;
        }

        const interpreterDetails = await getInterpreterDetails();
        if (interpreterDetails.path && interpreterDetails.path[0].includes(benchLocation)) {
            traceVerbose(`Using interpreter from Python extension: ${interpreterDetails.path.join(' ')}`);

            lsClient = await restartServer(serverId, serverName, outputChannel, benchLocation, lsClient);
            treeViewHelper = new TreeViewHelper(lsClient!);
            const appTreeViewProvider = new FrappeTreeViewProvider(treeViewHelper);
            vscode.window.createTreeView('frappe_apps', {
                treeDataProvider: appTreeViewProvider
            });
            return;
        }

        traceError(
            'Python interpreter missing:\r\n' +
            '[Option 1] Select python interpreter using the ms-python.python.\r\n' +
            `[Option 2] Set an interpreter using "${serverId}.interpreter" setting.\r\n` +
            'Please use Python 3.8 or greater.',
        );
    };
    context.subscriptions.push(
        onDidChangePythonInterpreter(async () => {
            await runServer();
        }),
        onDidChangeConfiguration(async (e: vscode.ConfigurationChangeEvent) => {
            if (checkIfConfigurationChanged(e, serverId)) {
                await runServer();
            }
        }),
        registerCommand(`${serverId}.restart`, async () => {
            await runServer();
        }),
    );

    setImmediate(async () => {
        const interpreter = getInterpreterFromSetting(serverId);
        if (interpreter === undefined || interpreter.length === 0) {
            traceLog(`Python extension loading`);
            await initializePython(context.subscriptions);
            traceLog(`Python extension loaded`);
        } else {
            await runServer();
        }
    });
}

export async function deactivate(): Promise<void> {
    if (lsClient) {
        await lsClient.stop();
    }
}
