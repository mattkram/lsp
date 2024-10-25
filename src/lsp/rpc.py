from lsp.schema import Message, ReceivedMessage


def encode_message(message: Message) -> bytes:
    content = message.model_dump_json()
    return f"Content-Length: {len(content)}\r\n\r\n{content}".encode("utf-8")


def decode_message(message: bytes) -> tuple[str, bytes]:
    header, sep, content = message.partition(b"\r\n\r\n")
    if not sep:
        raise ValueError("Did not find separator")

    content_length = int(header[len("Content-Length: ") :])

    content = content[:content_length]
    model = ReceivedMessage.model_validate_json(content.decode("utf-8"))
    return model.method, content
