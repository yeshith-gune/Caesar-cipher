"""
Caesar Cipher — encrypt, decrypt, and brute-force cracker.
"""

ALPHABET = "abcdefghijklmnopqrstuvwxyz"
ALPHA_LEN = len(ALPHABET)

# Common English words used by the frequency scorer
COMMON_WORDS = {
    "the", "be", "to", "of", "and", "a", "in", "that", "have", "it",
    "for", "not", "on", "with", "he", "as", "you", "do", "at", "this",
    "but", "his", "by", "from", "they", "we", "say", "her", "she", "or",
    "an", "will", "my", "one", "all", "would", "there", "their", "what",
    "so", "up", "out", "if", "about", "who", "get", "which", "go", "me",
    "is", "was", "are", "been", "has", "had", "were", "said", "did", "may",
}

# Approximate English letter frequencies (%) for scoring
ENGLISH_FREQ = {
    'e': 12.70, 't': 9.06, 'a': 8.17, 'o': 7.51, 'i': 6.97, 'n': 6.75,
    's': 6.33, 'h': 6.09, 'r': 5.99, 'd': 4.25, 'l': 4.03, 'c': 2.78,
    'u': 2.76, 'm': 2.41, 'w': 2.36, 'f': 2.23, 'g': 2.02, 'y': 1.97,
    'p': 1.93, 'b': 1.29, 'v': 0.98, 'k': 0.77, 'j': 0.15, 'x': 0.15,
    'q': 0.10, 'z': 0.07,
}


# ─────────────────────────────────────────────
# Core cipher functions
# ─────────────────────────────────────────────

def _shift_char(char: str, shift: int) -> str:
    """Shift a single character by *shift* positions (handles upper/lower)."""
    if char.isalpha():
        base = ord('A') if char.isupper() else ord('a')
        return chr((ord(char) - base + shift) % ALPHA_LEN + base)
    return char                     # digits, punctuation, spaces unchanged


def encrypt(plaintext: str, shift: int) -> str:
    """Encrypt *plaintext* with a Caesar shift of *shift* (1–25)."""
    shift = shift % ALPHA_LEN       # normalise (handles negatives too)
    return "".join(_shift_char(ch, shift) for ch in plaintext)


def decrypt(ciphertext: str, shift: int) -> str:
    """Decrypt *ciphertext* that was encrypted with *shift*."""
    return encrypt(ciphertext, -shift)


# ─────────────────────────────────────────────
# Scoring helpers
# ─────────────────────────────────────────────

def _letter_frequency_score(text: str) -> float:
    """
    Chi-squared–like distance from English frequencies.
    Lower = more English-like.  Returns negative so higher = better.
    """
    lower = text.lower()
    total = sum(1 for c in lower if c.isalpha())
    if total == 0:
        return float('-inf')

    score = 0.0
    for ch in ALPHABET:
        observed = lower.count(ch) / total * 100
        expected = ENGLISH_FREQ[ch]
        score -= (observed - expected) ** 2 / expected     # chi-squared term
    return score


def _word_score(text: str) -> int:
    """Count how many common English words appear in *text*."""
    words = text.lower().split()
    return sum(1 for w in words if w.strip(".,!?;:'\"") in COMMON_WORDS)


def score_text(text: str) -> float:
    """
    Combined heuristic score.  Higher = more likely to be English.
    Weighs word matching heavily because it's very reliable.
    """
    return _letter_frequency_score(text) + _word_score(text) * 5.0


# ─────────────────────────────────────────────
# Brute-force cracker
# ─────────────────────────────────────────────

def brute_force(ciphertext: str, top_n: int = 3) -> list[dict]:
    """
    Try all 25 possible shifts and rank results by English likelihood.

    Returns a list of dicts (sorted best-first), each containing:
        shift      – the shift key tried
        score      – heuristic score (higher = better)
        plaintext  – decrypted text for this shift
    """
    results = []
    for shift in range(1, ALPHA_LEN):
        candidate = decrypt(ciphertext, shift)
        results.append({
            "shift":     shift,
            "score":     score_text(candidate),
            "plaintext": candidate,
        })

    results.sort(key=lambda r: r["score"], reverse=True)
    return results[:top_n]
