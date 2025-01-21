class FunctionDetails:
    name: str
    func_call: any
    current_argument_index: int = 0
    args = {}
    kwargs = {}

    def __init__(
        self,
        name: str,
        func_call: str,
        current_argument_index: int,
        args: dict[str, any],
        kwargs: dict[str, any],
    ):
        self.name = name
        self.func_call = func_call
        self.current_argument_index = current_argument_index
        self.args = args
        self.kwargs = kwargs
