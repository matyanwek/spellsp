import functools
from typing import Any
from pathlib import Path
from dataclasses import dataclass

from .structures import (
    Range,
    Diagnostic,
    PublishDiagnosticParams,
    JsonrpcStream,
)


def splitwords(line: str) -> list[tuple[int, str]]:
    words: list[tuple[int, str]] = []
    word: list[str] = []
    offset = 0
    for i, char in enumerate(line):
        if not char.isalpha():
            if word:
                words.append((offset, "".join(word)))
                word.clear()
        else:
            if not word:
                offset = i
            word.append(char)
    if word:
        words.append((offset, "".join(word)))
    return words


def make_wordbag(buffer: str) -> list[tuple[int, int, str]]:
    """turn a buffer into words indexed by their (line, offset) position"""
    return [
        (linenum, offset, word)
        for (linenum, line) in enumerate(buffer.splitlines())
        for (offset, word) in splitwords(line)
    ]


def detitle(word: str) -> str:
    """uncapitalize first letter of word"""
    return word[0].lower() + word[1:]


# TODO: corrections
def check_spelling(buffer: str, wordset: set[str]) -> list[Range]:
    """return ranges of spelling errors"""
    return [
        Range.from_word(line, offset, word)
        for line, offset, word in make_wordbag(buffer)
        if word not in wordset and detitle(word) not in wordset
    ]
