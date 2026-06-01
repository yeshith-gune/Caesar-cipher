#!/usr/bin/env python3
"""
caesar_cli.py  –  Command-line interface for the Caesar cipher tool.

Usage examples:
    python caesar_cli.py encrypt "Hello, World!" 13
    python caesar_cli.py decrypt "Uryyb, Jbeyq!" 13
    python caesar_cli.py crack  "Khoor, Zruog!"
    python caesar_cli.py crack  "Khoor, Zruog!" --top 5
"""


import argparse
from caesar import encrypt, decrypt, brute_force
import sys
from pathlib import Path

# Allow running from repo root or src/
sys.path.insert(0, str(Path(__file__).parent / "src"))


# ─────────────────────────────────────────────
# Formatters
# ─────────────────────────────────────────────

def _header(title: str) -> str:
    line = "─" * (len(title) + 4)
    return f"\n{line}\n  {title}\n{line}"


def _print_crack_results(results: list[dict]) -> None:
    print(_header("Brute-force results (best guesses first)"))
    for rank, r in enumerate(results, start=1):
        print(f"\n  #{rank}  shift={r['shift']:>2}  score={r['score']:>7.2f}")
        preview = r["plaintext"][:80] + \
            ("…" if len(r["plaintext"]) > 80 else "")
        print(f"       {preview}")
    print()


# ─────────────────────────────────────────────
# CLI entry point
# ─────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="caesar_cli",
        description="Caesar cipher: encrypt, decrypt, or crack ciphertext.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s encrypt "Meet me at midnight" 7
  %(prog)s decrypt "Tlla tl ha tpkupnoa" 7
  %(prog)s crack   "Khoor, Zruog!"
  %(prog)s crack   "Khoor, Zruog!" --top 5
        """,
    )

    sub = parser.add_subparsers(dest="command", metavar="COMMAND")
    sub.required = True

    # encrypt
    enc = sub.add_parser("encrypt", help="Encrypt plaintext with a shift key")
    enc.add_argument("text",  help="Text to encrypt")
    enc.add_argument("shift", type=int, help="Shift key (1-25)")

    # decrypt
    dec = sub.add_parser("decrypt", help="Decrypt ciphertext with a shift key")
    dec.add_argument("text",  help="Text to decrypt")
    dec.add_argument("shift", type=int,
                     help="Shift key used during encryption")

    # crack
    crack = sub.add_parser("crack", help="Brute-force crack ciphertext")
    crack.add_argument("text", help="Ciphertext to crack")
    crack.add_argument(
        "--top", "-n",
        type=int, default=3, dest="top_n",
        metavar="N",
        help="Show top N candidates (default: 3)",
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "encrypt":
        result = encrypt(args.text, args.shift)
        print(_header(f"Encrypted  (shift={args.shift})"))
        print(f"\n  {result}\n")

    elif args.command == "decrypt":
        result = decrypt(args.text, args.shift)
        print(_header(f"Decrypted  (shift={args.shift})"))
        print(f"\n  {result}\n")

    elif args.command == "crack":
        print(_header(f"Cracking…  (testing all 25 shifts)"))
        results = brute_force(args.text, top_n=args.top_n)
        _print_crack_results(results)


if __name__ == "__main__":
    main()
