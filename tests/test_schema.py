import json

from lsp import rpc
from lsp import schema


def test_initalize_response():
    data = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "capabilities": {},
            "serverInfo": {
                "name": "kramer-lsp",
                "version": "0.0.0",
            },
        },
    }
    content = json.dumps(data).encode("utf-8")
    model = schema.InitializeResponse.model_validate_json(content)
    assert model.model_dump(by_alias=True) == data

    message = rpc.encode_message(model)

    expected_content = '{"jsonrpc":"2.0","id":1,"result":{"capabilities":{},"serverInfo":{"name":"kramer-lsp","version":"0.0.0"}}}'
    expected_message = (
        f"Content-Length: {len(expected_content)}\r\n\r\n{expected_content}"
    )
    assert message.decode("utf-8") == expected_message
