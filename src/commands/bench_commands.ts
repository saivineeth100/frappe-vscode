import * as vscode from 'vscode';

export  function benchcommandsRunner(command: string, args: string | null = null) {
    try {
        const cp = require('child_process');
        let argument = args;
        let operation: string = command + ' ' + argument;
        let cmd = 'bench ' + (args == null ? command : operation);
        const proc =  cp.spawnSync(cmd, {
            shell: true,
            encoding: 'utf8',
        });
        let procData = "";
        if (proc !== null) {
            if (proc.stdout !== null && proc.stdout.toString() !== '') {
                procData = proc.stdout.toString();
            }
            if (proc.stderr !== null && proc.stderr.toString() !== '') {
                const procErr = proc.stderr.toString;
                // MessageUtils.showErrorMessage("The '" + operation + "' process failed: " + procErr);
                procData = procErr;
            }
        }
        return procData;
    } catch (error) {

        return null
    }
}
export  function runBenchFindCommand() {
    try {
        let resp =  benchcommandsRunner("find")
        return resp?.replace(" found!\n","")

    } catch (error) {
        throw error
    }
}