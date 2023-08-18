import logging
import functools
from pathlib import Path
from typing import Any, Optional, Protocol, TextIO

from .structures import (
    JsonrpcStream,
    TextDocument,
    Diagnostic,
    PublishDiagnosticParams,
)
from .spellcheck import check_spelling

INIT_RESULT = {
    "capabilities": {
        "PositionEncoding": "utf-8",
        "diagnosticProvider": {
            "identifier": "Spelling",
            "interFileDependencies": False,
            "workspaceDiagnostics": False,
        },
        "textDocumentSync": 1,
    },
    "serverInfo": {
        "name": "spellsp",
        # "version": "0.1",
    },
}


def shutdown(stream: JsonrpcStream) -> None:
    if stream.last_message.get("method") == "shutdown":
        stream.send_response(stream.last_message.get("id"), None)
    logging.info("shutting down...")
    stream.read_message()
    while stream.last_message.get("method") != "exit":
        logging.error("request received after shutdown")
        stream.send_error(
            stream.last_message.get("id"),
            {"code": -32700, "message": "shutting down; awaiting exit request"},
        )
        stream.read_message()
    logging.info("exiting")
    stream.close()
    exit(0)


def initialize(stream: JsonrpcStream) -> None:
    stream.read_message()
    if stream.last_message.get("method") != "initialize":
        logging.error("request received before initialization")
        stream.send_error(None, {"code": -32002, "message": "not initialized"})
        logging.info("shutting down...")
        stream.read_message()
        while stream.last_message.get("method") != "exit":
            stream.read_message()
        logging.info("exiting")
        stream.close()
        exit(0)
    logging.info("initializing...")
    stream.send_response(stream.last_message["id"], INIT_RESULT)
    stream.read_message()
    while stream.last_message.get("method") != "initialized":
        stream.read_message()
    logging.info("initialized")


def extract_doc(message_params: dict[Any, Any]) -> TextDocument:
    """extract textDocument data from notifications"""
    doc_params = message_params["textDocument"]
    uri = doc_params.get("uri")
    version = doc_params.get("version")
    text = doc_params.get("text")
    if text is None:
        text = message_params["contentChanges"][0]["text"]
    return TextDocument(uri, text, version)


def publish_diagnostics(stream: JsonrpcStream, wordset: set[str]) -> None:
    doc = extract_doc(stream.last_message["params"])
    diagnostics = [
        Diagnostic(spell_range) for spell_range in check_spelling(doc.text, wordset)
    ]
    publish_params = PublishDiagnosticParams(
        uri=doc.uri,
        diagnostics=diagnostics,
        version=doc.version,
    )
    stream.send_notification("textDocument/publishDiagnostics", publish_params)


# TODO: affixes, proper capitalization detection
def make_wordset(path: Path) -> set[str]:
    """simplified word list spell checking"""
    with path.open() as f:
        return {line.strip().split("/", 1)[0] for line in f}


def dispatch(stream: JsonrpcStream, wordset_path: Path) -> None:
    wordset = make_wordset(wordset_path)
    initialize(stream)
    while stream.read_message():
        match stream.last_message["method"]:
            case "shutdown":
                break
            case "exit":
                exit(1)  # did not receive "shutdown" request; exit with code 1
            case "textDocument/didOpen" | "textDocument/didChange":
                publish_diagnostics(stream, wordset)
    shutdown(stream)
