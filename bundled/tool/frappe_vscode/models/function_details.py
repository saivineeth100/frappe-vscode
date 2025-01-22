class FunctionArgument:
    arg_value: any
    string_value: str | None

    def __init__(self, arg_value, string_value=None):
        self.arg_value = arg_value
        self.string_value = string_value


class FunctionDetails:
    name: str
    func_call: any
    current_argument_index: int = 0
    args = {}
    kwargs = {}
    RecoveredSearchText: str | None

    def __init__(
        self,
        name: str,
        func_call: str,
        current_argument_index: int,
        args: dict[str, FunctionArgument],
        kwargs: dict[str, FunctionArgument],
        recovered_search_text: str | None,
    ):
        self.name = name
        self.func_call = func_call
        self.current_argument_index = current_argument_index
        self.args = args
        self.kwargs = kwargs
        self.RecoveredSearchText = recovered_search_text
