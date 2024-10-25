from typing import Any

from pydantic import BaseModel as _BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class BaseModel(_BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    def model_dump(self, **kwargs: Any) -> dict[str, Any]:
        by_alias = kwargs.pop("by_alias", True)
        return super().model_dump(by_alias=by_alias, **kwargs)

    def model_dump_json(self, **kwargs: Any) -> str:
        by_alias = kwargs.pop("by_alias", True)
        return super().model_dump_json(by_alias=by_alias, **kwargs)


class Message(BaseModel):
    jsonrpc: str = "2.0"


class Request(Message):
    id: int | str
    method: str

    # TODO: Params


class Notification(Message):
    jsonrpc: str
    method: str


class Response(Message):
    id: int | None = None

    # Result
    # Error


class ClientInfo(BaseModel):
    name: str
    version: str


class InitializeRequestParams(BaseModel):
    client_info: ClientInfo | None = None
    # There's tons more that goes here


class InitializeRequest(Request):
    params: InitializeRequestParams


class ServerCapabilities(BaseModel): ...


class ServerInfo(BaseModel):
    name: str
    version: str


class InitializeResult(BaseModel):
    capabilities: ServerCapabilities
    server_info: ServerInfo


class InitializeResponse(Response):
    result: InitializeResult
