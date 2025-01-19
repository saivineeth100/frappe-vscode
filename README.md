# Frappe Framework Support for VSCode

## Building and Run the extension

Run the `Debug Extension and Python` configuration form VS Code. That should build and debug the extension in host window.

Note: if you just want to build you can run the build task in VS Code (`ctrl`+`shift`+`B`)

## Debugging

To debug both TypeScript and Python code use `Debug Extension and Python` debug config. This is the recommended way. Also, when stopping, be sure to stop both the Typescript, and Python debug sessions. Otherwise, it may not reconnect to the python session.

To debug only TypeScript code, use `Debug Extension` debug config.

To debug a already running server or in production server, use `Python Attach`, and select the process that is running `lsp_server.py`.

## Logging and Logs

logging Output channel that can be found under `Output` > `frappe-vscode` panel. You can control the log level running the `Developer: Set Log Level...` command from the Command Palette, and selecting your extension from the list. It should be listed using the display name for your tool. You can also set the global log level, and that will apply to all extensions and the editor.

If you need logs that involve messages between the Language Client and Language Server, you can set `"frappe-vscode.server.trace": "verbose"`, to get the messaging logs. These logs are also available `Output` > `frappe-vscode` panel.


## Testing

See `src/test/python_tests/test_server.py` for starting point. See, other referred projects here for testing various aspects of running the tool over LSP.

If you have installed the test requirements you should be able to see the tests in the test explorer.

You can also run all tests using `nox --session tests` command.

## Linting

Run `nox --session lint` to run linting on both Python and TypeScript code. Please update the nox file if you want to use a different linter and formatter.
