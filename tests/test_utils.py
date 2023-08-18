import json
from typing import Any


def make_msg(obj: dict[Any, Any]) -> str:
    obj["jsonrpc"] = "2.0"
    body = json.dumps(obj)
    return f"Content-Length: {len(body)}\r\n\r\n{body}"


def parse_msg(message: str) -> dict[Any, Any]:
    header, body = message.split("\r\n\r\n")
    [content_length] = [
        int(line.removeprefix("Content-Length: "))
        for line in header.splitlines()
        if line.startswith("Content-Length: ")
    ]
    return json.loads(body[:content_length])
