import unittest
import unittest.mock as mock
from dataclasses import dataclass

from src.spellsp.structures import Range, Position
from src.spellsp.spellcheck import check_spelling


class TestSpellcheck(unittest.TestCase):
    def test_check_spelling_regular(self) -> None:
        wordset = {"cat", "hat"}
        sentence = "the cat in the hat"
        expected_ranges = [
            Range.from_word(0, 0, "the"),
            Range.from_word(0, 8, "in"),
            Range.from_word(0, 11, "the"),
        ]
        self.assertEqual(check_spelling(sentence, wordset), expected_ranges)

    def test_check_spelling_proper_noun(self) -> None:
        wordset = {"Cat", "Hat"}
        sentence = "the cat in the Hat"
        expected_ranges = [
            Range.from_word(0, 0, "the"),
            Range.from_word(0, 4, "cat"),
            Range.from_word(0, 8, "in"),
            Range.from_word(0, 11, "the"),
        ]
        self.assertEqual(check_spelling(sentence, wordset), expected_ranges)

    def test_check_spelling_capitalized(self) -> None:
        wordset = {"the", "cat", "hat"}
        sentence = "The cat in the hat"
        expected_ranges = [
            Range.from_word(0, 8, "in"),
        ]
        self.assertEqual(check_spelling(sentence, wordset), expected_ranges)

    def test_check_spelling_capitalized_improperly(self) -> None:
        wordset = {"the", "cat", "hat"}
        sentence = "tHe cat in the hat"
        expected_ranges = [
            Range.from_word(0, 0, "the"),
            Range.from_word(0, 8, "in"),
        ]
        self.assertEqual(check_spelling(sentence, wordset), expected_ranges)


if __name__ == "__main__":
    unittest.main()
