"""SPECTRE - Reverse engineering CLI."""
from __future__ import annotations
import argparse, json, sys
from dataclasses import asdict
from pathlib import Path
from .recon import Recon
from .disect import Disect
from .strings import Strings
from .entropy import EntropyAnalyzer
from .carve import Carver
from .trace import Trace


def cmd_info(a):
    print(json.dumps(asdict(Recon.inspect(a.file)), indent=2, default=str))

def cmd_hex(a):
    print(Recon.hex_dump(a.file, offset=a.offset, length=a.length))

def cmd_header(a):
    print(json.dumps(asdict(Disect.parse(a.file)), indent=2, default=str))

def cmd_strings(a):
    s = Strings(min_length=a.min_length)
    seen = set()
    for enc, text in s.extract(a.file):
        if text in seen: continue
        seen.add(text)
        print(f"[{enc}] {text}")

def cmd_entropy(a):
    print(json.dumps(EntropyAnalyzer().summary(a.file, block_size=a.block), indent=2))

def cmd_carve(a):
    print(json.dumps(Carver().carve_file(a.file), indent=2))

def cmd_trace(a):
    data = Path(a.file).read_bytes()
    print(json.dumps(Trace.bruteforce_single(data, top=a.top), indent=2))


def main(argv=None):
    p = argparse.ArgumentParser(prog="spectre",
        description="AETHER-QM SPECTRE - reverse engineering toolkit")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("info"); s.add_argument("file"); s.set_defaults(func=cmd_info)
    s = sub.add_parser("hex"); s.add_argument("file")
    s.add_argument("--offset", type=int, default=0)
    s.add_argument("--length", type=int, default=512); s.set_defaults(func=cmd_hex)
    s = sub.add_parser("header"); s.add_argument("file"); s.set_defaults(func=cmd_header)
    s = sub.add_parser("strings"); s.add_argument("file")
    s.add_argument("--min-length", type=int, default=4); s.set_defaults(func=cmd_strings)
    s = sub.add_parser("entropy"); s.add_argument("file")
    s.add_argument("--block", type=int, default=4096); s.set_defaults(func=cmd_entropy)
    s = sub.add_parser("carve"); s.add_argument("file"); s.set_defaults(func=cmd_carve)
    s = sub.add_parser("trace"); s.add_argument("file")
    s.add_argument("--top", type=int, default=10); s.set_defaults(func=cmd_trace)

    args = p.parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
