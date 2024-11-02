from typing import Callable
from lsp.schema import Response

MethodName = str
HandlerFunc = Callable[[bytes], Response | None]
