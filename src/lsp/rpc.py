from pydantic import BaseModel


class BaseMessage(BaseModel):
    method: str


def encode_message(message: BaseModel) -> str:
    content = message.model_dump_json()
    return f"Content-Length: {len(content)}\r\n\r\n{content}"


def decode_message(message: str) -> BaseMessage:
    header, sep, content = message.partition("\r\n\r\n")
    if not sep:
        raise ValueError("Did not find separator")

    content_length = int(header[len("Content-Length: "):])

    content = content[:content_length]
    model = BaseMessage.model_validate_json(content)
    return model.method, content
