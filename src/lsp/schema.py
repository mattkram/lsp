from pydantic import BaseModel as _BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class BaseModel(_BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)


class Request(BaseModel):
    jsonrpc: str
    id: int
    method: str

    # Params


class Response(BaseModel):
    jsonrpc: str
    id: int | None = None

    # Result
    # Error


class Notification(BaseModel):
    jsonrpc: str
    method: str


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
