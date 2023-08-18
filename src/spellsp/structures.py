from __future__ import annotations
import json
import functools
from dataclasses import dataclass
from typing import Any, Optional, Protocol, TextIO


class AsJson(Protocol):
    def as_json(self) -> dict[Any, Any]:
        ...


Jsonable = dict[Any, Any] | AsJson


class ObjEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        try:
            return obj.as_json()
        except AttributeError:
            return json.JSONEncoder.default(self, obj)


dump = functools.partial(json.dumps, cls=ObjEncoder)


class JsonrpcStream:
    def __init__(self, input_stream: TextIO, output_stream: TextIO) -> None:
        self._instream = input_stream
        self._outstream = output_stream
        self._last_message: dict[Any, Any] = {}

    @property
    def last_message(self) -> dict[Any, Any]:
        return self._last_message

    def close(self) -> None:
        self._instream.close()
        self._outstream.close()

    def _read_stream(self) -> str:
        # get content length
        line = self._instream.readline()
        while not line.startswith("Content-Length:"):
            line = self._instream.readline()
        value = line.removeprefix("Content-Length: ").strip()
        try:
            content_length = int(value)
        except ValueError as error:
            raise ValueError(f"invalid content length {value}") from error
        # skip rest of header
        while line.strip():
            line = self._instream.readline()
        # read content
        return self._instream.read(content_length)

    def read_message(self) -> dict[Any, Any]:
        self._last_message = json.loads(self._read_stream())
        return self.last_message

    def _write_message(self, obj: dict[Any, Any]) -> None:
        obj["jsonrpc"] = "2.0"
        msg = dump(obj)
        self._outstream.write(f"Content-Length: {len(msg)}\r\n\r\n{msg}")
        self._outstream.flush()

    def send_response(self, id: int | None, result: Optional[Jsonable] = None) -> None:
        self._write_message({"id": id, "result": result})

    def send_error(self, id: int | None, error: Jsonable) -> None:
        self._write_message({"id": id, "error": error})

    def send_notification(self, method: str, params: Optional[Jsonable] = None) -> None:
        self._write_message({"method": method, "params": params})

    def send_request(
        self, id: int | None, method: str, params: Optional[Jsonable] = None
    ) -> None:
        self._write_message({"id": id, "method": method, "params": params})


@dataclass
class Position:
    line: int
    char: int

    def as_json(self) -> dict[str, int]:
        return {"line": self.line, "character": self.char}


@dataclass
class Range:
    start: Position
    end: Position

    @staticmethod
    def from_word(line: int, offset: int, word: str) -> Range:
        start = Position(line, offset)
        end = Position(line, offset + len(word))
        return Range(start, end)

    def as_json(self) -> dict[str, dict[str, int]]:
        return {"start": self.start.as_json(), "end": self.end.as_json()}


@dataclass
class Diagnostic:
    range_: Range
    message: str = ""
    severity: int = 1

    def as_json(self) -> dict[str, Any]:
        return {
            "range": self.range_.as_json(),
            "message": self.message,
            "severity": self.severity,
        }


@dataclass
class TextDocument:
    uri: str
    text: str
    version: int


@dataclass
class PublishDiagnosticParams:
    uri: str
    diagnostics: list[Diagnostic]
    version: Optional[int] = None

    def as_json(self) -> dict[str, Any]:
        return {
            "uri": self.uri,
            "version": self.version,
            "diagnostics": [diagnostic.as_json() for diagnostic in self.diagnostics],
        }
