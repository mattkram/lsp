import pytest
from pydantic import BaseModel

from lsp.rpc import encode_message, decode_message


class Message(BaseModel):
    field: str


def test_encode_message():
    actual = encode_message(Message(field="hello"))
    expected = 'Content-Length: 17\r\n\r\n{"field":"hello"}'
    assert actual == expected


def test_decode_message():
    message = 'Content-Length: 15\r\n\r\n{"method":"hi"}'
    method, content= decode_message(message)
    content_length = len(content)
    assert content_length == 15
    assert method == "hi"


def test_decode_message_raises_on_missing_separator():
    with pytest.raises(ValueError):
        decode_message("")
