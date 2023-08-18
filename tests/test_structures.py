import io
import json
import unittest
import unittest.mock as mock
from typing import Any

from src.spellsp.structures import (
    JsonrpcStream,
    Position,
    Range,
    Diagnostic,
    PublishDiagnosticParams,
)

from .test_utils import make_msg, parse_msg


class TestStream(unittest.TestCase):
    def setUp(self) -> None:
        self.instream = io.StringIO()
        self.outstream = io.StringIO()
        self.jsonstream = JsonrpcStream(self.instream, self.outstream)

    def test_close(self) -> None:
        self.jsonstream.close()
        self.assertEqual(self.instream.closed, True)
        self.assertEqual(self.outstream.closed, True)

    def test_read_message(self) -> None:
        expected_obj = {"jsonrpc": "2.0", "hello": "world"}
        self.instream.write(make_msg(expected_obj))
        self.instream.seek(0)
        self.assertEqual(self.jsonstream.read_message(), expected_obj)

    def test_last_message(self) -> None:
        self.assertEqual(self.jsonstream.last_message, {})
        self.instream.write(make_msg({"hello": "world"}))
        self.instream.seek(0)
        read_message = self.jsonstream.read_message()
        self.assertEqual(self.jsonstream.last_message, read_message)

    def test_send_response(self) -> None:
        id = 1
        result = {"hello": "world"}
        self.jsonstream.send_response(id, result)
        self.outstream.seek(0)
        expected_obj = {"jsonrpc": "2.0", "id": id, "result": result}
        self.assertEqual(parse_msg(self.outstream.read()), expected_obj)

    def test_send_error(self) -> None:
        id = 1
        error = {"code": -1, "message": "error"}
        self.jsonstream.send_error(id, error)
        self.outstream.seek(0)
        expected_obj = {"jsonrpc": "2.0", "id": id, "error": error}
        self.assertEqual(parse_msg(self.outstream.read()), expected_obj)

    def test_send_notification(self) -> None:
        method = "method"
        params = {"hello": "world"}
        self.jsonstream.send_notification(method, params)
        self.outstream.seek(0)
        expected_obj = {"jsonrpc": "2.0", "method": method, "params": params}
        self.assertEqual(parse_msg(self.outstream.read()), expected_obj)

    def test_send_request(self) -> None:
        id = 1
        method = "method"
        params = {"hello": "world"}
        self.jsonstream.send_request(id, method, params)
        self.outstream.seek(0)
        expected_obj = {"jsonrpc": "2.0", "id": id, "method": method, "params": params}
        self.assertEqual(parse_msg(self.outstream.read()), expected_obj)


class TestAsJson(unittest.TestCase):
    def test_position(self) -> None:
        line = 10
        char = 41
        pos = Position(line, char)
        expected_obj = {"line": line, "character": char}
        self.assertEqual(pos.as_json(), expected_obj)

    def test_range(self) -> None:
        l1 = 10
        c1 = 0
        l2 = 10
        c2 = 12
        p1 = Position(l1, c1)
        p2 = Position(l2, c2)
        r = Range(p1, p2)
        expected_obj = {"start": p1.as_json(), "end": p2.as_json()}
        self.assertEqual(r.as_json(), expected_obj)

    def test_diagnostic(self) -> None:
        l1 = 10
        c1 = 0
        l2 = 10
        c2 = 12
        r = Range(Position(l1, c1), Position(l2, c2))
        message = "diagnostic message"
        severity = 1
        version = 1
        diagnostic = Diagnostic(r, message, severity)
        expected_obj = {
            "range": r.as_json(),
            "message": message,
            "severity": severity,
        }
        self.assertEqual(diagnostic.as_json(), expected_obj)

    def test_diagnostic_params(self) -> None:
        message = "diagnostic message"
        severity = 1
        version = 1
        positions = [(0, 0), (0, 12), (1, 0), (2, 3)]
        diagnostics = [
            Diagnostic(Range(Position(0, 0), Position(0, 12)), message, severity),
            Diagnostic(Range(Position(1, 0), Position(1, 12)), message, severity),
            Diagnostic(Range(Position(2, 0), Position(2, 12)), message, severity),
        ]
        uri = "file"
        params = PublishDiagnosticParams(uri, diagnostics, version)
        expected_obj = {
            "uri": uri,
            "version": version,
            "diagnostics": [diagnostic.as_json() for diagnostic in diagnostics],
        }
        self.assertEqual(params.as_json(), expected_obj)


if __name__ == "__main__":
    unittest.main()
