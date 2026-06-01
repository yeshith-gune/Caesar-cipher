"""
tests/test_caesar.py  –  pytest test suite for the Caesar cipher module.
Run with:  pytest tests/ -v
"""

from caesar import encrypt, decrypt, brute_force, score_text
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


# ──────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────

PANGRAM = "The quick brown fox jumps over the lazy dog"


# ──────────────────────────────────────────────────────────────
# encrypt()
# ──────────────────────────────────────────────────────────────

class TestEncrypt:
    def test_rot13(self):
        assert encrypt("Hello", 13) == "Uryyb"

    def test_shift_3(self):
        assert encrypt("ABC", 3) == "DEF"

    def test_preserves_case(self):
        result = encrypt("Hello World", 1)
        assert result == "Ifmmp Xpsme"

    def test_non_alpha_unchanged(self):
        result = encrypt("Hello, World! 123", 3)
        assert result == "Khoor, Zruog! 123"

    def test_wrap_around(self):
        assert encrypt("xyz", 3) == "abc"

    def test_shift_zero_identity(self):
        assert encrypt(PANGRAM, 0) == PANGRAM

    def test_shift_26_identity(self):
        assert encrypt(PANGRAM, 26) == PANGRAM

    def test_shift_normalised(self):
        # shift 27 == shift 1
        assert encrypt("abc", 27) == encrypt("abc", 1)

    def test_empty_string(self):
        assert encrypt("", 5) == ""

    def test_full_pangram(self):
        cipher = encrypt(PANGRAM, 4)
        assert decrypt(cipher, 4) == PANGRAM


# ──────────────────────────────────────────────────────────────
# decrypt()
# ──────────────────────────────────────────────────────────────

class TestDecrypt:
    def test_rot13_roundtrip(self):
        cipher = encrypt("Hello, World!", 13)
        assert decrypt(cipher, 13) == "Hello, World!"

    def test_inverse_of_encrypt(self):
        for shift in range(1, 26):
            assert decrypt(encrypt(PANGRAM, shift), shift) == PANGRAM

    def test_preserves_non_alpha(self):
        assert decrypt("Khoor, Zruog! 123", 3) == "Hello, World! 123"


# ──────────────────────────────────────────────────────────────
# brute_force()
# ──────────────────────────────────────────────────────────────

class TestBruteForce:
    PLAIN = "The cat sat on the mat and the rat ran away from the flat"

    def test_correct_shift_in_top1(self):
        for shift in [3, 7, 13, 19]:
            cipher = encrypt(self.PLAIN, shift)
            results = brute_force(cipher, top_n=1)
            assert results[0]["shift"] == shift, (
                f"Expected shift={shift}, got {results[0]['shift']}"
            )

    def test_returns_top_n(self):
        cipher = encrypt(self.PLAIN, 5)
        for n in [1, 3, 5]:
            assert len(brute_force(cipher, top_n=n)) == n

    def test_results_sorted_descending(self):
        cipher = encrypt(self.PLAIN, 3)
        results = brute_force(cipher, top_n=5)
        scores = [r["score"] for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_plaintext_field_populated(self):
        cipher = encrypt("Hello world", 3)
        for r in brute_force(cipher):
            assert isinstance(r["plaintext"], str)
            assert len(r["plaintext"]) > 0

    def test_correct_plaintext_in_result(self):
        plain = "attack at dawn"
        shift = 11
        cipher = encrypt(plain, shift)
        results = brute_force(cipher, top_n=1)
        assert results[0]["plaintext"].lower() == plain.lower()


# ──────────────────────────────────────────────────────────────
# score_text()
# ──────────────────────────────────────────────────────────────

class TestScoreText:
    def test_english_scores_higher_than_cipher(self):
        english = PANGRAM
        cipher = encrypt(PANGRAM, 7)
        assert score_text(english) > score_text(cipher)

    def test_empty_text(self):
        assert score_text("") == float('-inf')

    def test_common_words_boost_score(self):
        rich = "the cat sat on the mat"
        rare = "zzz xxx qqq yyy www"
        assert score_text(rich) > score_text(rare)
