import sys
import logging
import argparse
from pathlib import Path
from typing import TextIO

from .dispatch import dispatch
from .structures import JsonrpcStream


def parse_args(args: list[str]) -> tuple[TextIO, TextIO, Path]:
    """get dictionary path as arg"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f",
        "--file",
        type=Path,
        help="dictionary file; Hunspell format or a plain-text word list",
    )
    parser.add_argument(
        "-i", "--input", default=None, help="input handle; defaults to stdin"
    )
    parser.add_argument(
        "-o", "--output", default=None, help="output handle; defaults to stdout"
    )
    parsed_args = parser.parse_args(args)
    if parsed_args.input is None:
        input_stream = sys.stdin
    else:
        input_stream = open(parsed_args.input, "r")
    if parsed_args.output is None:
        output_stream = sys.stdout
    else:
        output_stream = open(parsed_args.output, "w")
    wordset_path = parsed_args.file
    return input_stream, output_stream, wordset_path


def main() -> None:
    logging.basicConfig(filename="spellsp.log", encoding="utf8", level=logging.DEBUG)
    logging.debug("\n\n")
    input_stream, output_stream, wordset_path = parse_args(sys.argv[1:])
    stream = JsonrpcStream(input_stream, output_stream)
    dispatch(stream, wordset_path=wordset_path)
