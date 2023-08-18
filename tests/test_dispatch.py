import io
import json
import tempfile
import unittest
import unittest.mock as mock
from pathlib import Path
from dataclasses import dataclass

from src.spellsp.dispatch import (
    INIT_RESULT,
    initialize,
    shutdown,
    publish_diagnostics,
    extract_doc,
    make_wordset,
)
from src.spellsp.structures import (
    JsonrpcStream,
    PublishDiagnosticParams,
    Diagnostic,
    Range,
)

from .test_utils import make_msg, parse_msg


class TestDispatch(unittest.TestCase):
    def setUp(self) -> None:
        self.instream = io.StringIO()
        self.outstream = io.StringIO()
        self.stream = JsonrpcStream(self.instream, self.outstream)

    def test_shutdown(self) -> None:
        self.instream.write(make_msg({"id": 0, "method": "shutdown"}))
        self.instream.write(make_msg({"method": "exit"}))
        self.instream.seek(0)
        self.stream.read_message()
        with self.assertRaises(SystemExit):
            shutdown(self.stream)
        self.outstream.seek(0)
        expected_response = {"jsonrpc": "2.0", "id": 0, "result": None}
        self.assertEqual(parse_msg(self.outstream.read()), expected_response)

    def test_shutdown_early(self) -> None:
        self.instream.write(make_msg({"method": "exit"}))
        self.instream.seek(0)
        with self.assertRaises(SystemExit):
            shutdown(self.stream)
        self.outstream.seek(0)
        self.assertEqual(self.outstream.read(), "")

    def test_shutdown_error(self) -> None:
        self.instream.write(make_msg({"id": 1, "method": "test"}))
        self.instream.write(make_msg({"method": "exit"}))
        self.instream.seek(0)
        with self.assertRaises(SystemExit):
            shutdown(self.stream)
        self.outstream.seek(0)
        expected_error = {
            "jsonrpc": "2.0",
            "id": 1,
            "error": {
                "code": -32700,
                "message": "shutting down; awaiting exit request",
            },
        }
        self.assertEqual(parse_msg(self.outstream.read()), expected_error)

    def test_initialize(self) -> None:
        self.instream.write(
            make_msg(
                {
                    "id": 0,
                    "method": "initialize",
                    "params": {
                        "processId": 1,
                        "rootUri": None,
                        "capabilities": {},
                    },
                }
            )
        )
        self.instream.write(make_msg({"method": "initialized", "params": {}}))
        self.instream.seek(0)
        initialize(self.stream)
        self.outstream.seek(0)
        expected_response = {"jsonrpc": "2.0", "id": 0, "result": INIT_RESULT}
        self.assertEqual(parse_msg(self.outstream.read()), expected_response)

    def test_initialize_error(self) -> None:
        self.instream.write(make_msg({"id": 0, "method": "test"}))
        self.instream.write(make_msg({"method": "exit"}))
        self.instream.seek(0)
        with self.assertRaises(SystemExit):
            initialize(self.stream)
        self.outstream.seek(0)
        expected_error = {
            "jsonrpc": "2.0",
            "id": None,
            "error": {"code": -32002, "message": "not initialized"},
        }
        self.assertEqual(parse_msg(self.outstream.read()), expected_error)

    def test_publish_diagnostics(self) -> None:
        self.instream.write(
            make_msg(
                {
                    "method": "textDocument/didOpen",
                    "params": {
                        "textDocument": {
                            "uri": "testfile",
                            "languageId": "text",
                            "version": 0,
                            "text": "the cat in the hat",
                        }
                    },
                }
            )
        )
        self.instream.seek(0)
        self.stream.read_message()
        publish_diagnostics(self.stream, {"cat", "hat"})
        self.outstream.seek(0)
        expected_diagnostics = {
            "jsonrpc": "2.0",
            "method": "textDocument/publishDiagnostics",
            "params": {
                "uri": "testfile",
                "version": 0,
                "diagnostics": [
                    {
                        "range": {
                            "start": {"line": 0, "character": 0},
                            "end": {"line": 0, "character": 3},
                        },
                        "severity": 1,
                        "message": "",
                    },
                    {
                        "range": {
                            "start": {"line": 0, "character": 8},
                            "end": {"line": 0, "character": 10},
                        },
                        "severity": 1,
                        "message": "",
                    },
                    {
                        "range": {
                            "start": {"line": 0, "character": 11},
                            "end": {"line": 0, "character": 14},
                        },
                        "severity": 1,
                        "message": "",
                    },
                ],
            },
        }
        self.maxDiff = None
        self.assertEqual(parse_msg(self.outstream.read()), expected_diagnostics)


class TestAuxFuncs(unittest.TestCase):
    def test_extract_doc_opened(self) -> None:
        uri = "testfile"
        text = "the cat in the hat.\n"
        version = 0
        params = {
            # "method": "textDocument/didOpen",
            # "params": {
            "textDocument": {
                "uri": uri,
                "languageId": "text",
                "version": version,
                "text": text,
            }
            # }
        }
        doc = extract_doc(params)
        self.assertEqual(doc.uri, uri)
        self.assertEqual(doc.version, version)
        self.assertEqual(doc.text, text)

    def test_extract_doc_changed(self) -> None:
        uri = "testfile"
        text = "the cat in the hat.\n"
        version = 1
        params = {
            # "method": "textDocument/didChange",
            # "params": {
            "contentChanges": [{"text": text}],
            "textDocument": {
                "uri": uri,
                "version": version,
            },
            # }
        }
        doc = extract_doc(params)
        self.assertEqual(doc.uri, uri)
        self.assertEqual(doc.version, version)
        self.assertEqual(doc.text, text)

    def test_make_wordset(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            file = Path(d) / "file.txt"
            file.write_text("cat\nhat/S\n")
            wordset = make_wordset(file)
        self.assertEqual(wordset, {"cat", "hat"})


if __name__ == "__main__":
    unittest.main()
