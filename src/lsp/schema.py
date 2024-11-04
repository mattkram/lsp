from enum import Enum
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


class ReceivedMessage(Message):
    method: str


class Request(ReceivedMessage):
    id: int | str

    # TODO: Params


class Notification(ReceivedMessage): ...


class Response(Message):
    id: int | str | None = None

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


class TextDocumentSyncKind(Enum):
    NONE: int = 0
    FULL: int = 1
    INCREMENTAL: int = 2


DocumentUri = str


class TextDocumentItem(BaseModel):
    uri: DocumentUri
    language_id: str
    version: int
    text: str


class DidOpenTextDocumentParams(BaseModel):
    text_document: TextDocumentItem


class DidOpenTextDocumentNotification(Notification):
    params: DidOpenTextDocumentParams


class TextDocumentIdentifier(BaseModel):
    uri: DocumentUri


class VersionedTextDocumentIdentifier(TextDocumentIdentifier):
    version: int


class TextDocumentContentChangeEvent(BaseModel):
    text: str


class DidChangeTextDocumentParams(BaseModel):
    text_document: VersionedTextDocumentIdentifier
    content_changes: list[TextDocumentContentChangeEvent] = []


class DidChangeTextDocument(Notification):
    params: DidChangeTextDocumentParams


class ServerCapabilities(BaseModel):
    text_document_sync: TextDocumentSyncKind = TextDocumentSyncKind.NONE


class ServerInfo(BaseModel):
    name: str
    version: str


class InitializeResult(BaseModel):
    capabilities: ServerCapabilities
    server_info: ServerInfo


class InitializeResponse(Response):
    result: InitializeResult
