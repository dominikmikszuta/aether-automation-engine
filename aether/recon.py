"""RECON - Binary reconnaissance."""
from __future__ import annotations
import hashlib, os
from dataclasses import dataclass, field
from pathlib import Path

MAGIC = {
    b"\x7fELF": "ELF", b"MZ": "PE/DOS",
    b"\xca\xfe\xba\xbe": "Mach-O", b"\xcf\xfa\xed\xfe": "Mach-O 64",
    b"PK\x03\x04": "ZIP", b"\x1f\x8b": "GZIP",
    b"BZh": "BZIP2", b"\xfd7zXZ\x00": "XZ",
    b"7z\xbc\xaf\x27\x1c": "7-Zip", b"Rar!\x1a\x07": "RAR",
    b"%PDF": "PDF", b"\x89PNG": "PNG",
    b"\xff\xd8\xff": "JPEG", b"GIF8": "GIF",
    b"SQLite format 3": "SQLite",
}

@dataclass
class BinaryInfo:
    path: str
    size: int
    magic: str = ""
    sha256: str = ""
    sha1: str = ""
    md5: str = ""
    entropy: float = 0.0
    is_executable: bool = False
    notes: list = field(default_factory=list)

class Recon:
    @staticmethod
    def _entropy(data):
        if not data: return 0.0
        from math import log2
        freq = [0] * 256
        for b in data: freq[b] += 1
        n = len(data)
        return -sum((c/n) * log2(c/n) for c in freq if c)

    @staticmethod
    def _magic(head):
        for sig, name in MAGIC.items():
            if head.startswith(sig): return name
        return "unknown"

    @classmethod
    def inspect(cls, path, max_read=1024*1024):
        path = Path(path)
        if not path.exists(): raise FileNotFoundError(path)
        size = path.stat().st_size
        head = path.read_bytes()[:max_read]
        info = BinaryInfo(path=str(path), size=size)
        info.magic = cls._magic(head)
        info.sha256 = hashlib.sha256(head).hexdigest()
        info.sha1 = hashlib.sha1(head).hexdigest()
        info.md5 = hashlib.md5(head).hexdigest()
        info.entropy = round(cls._entropy(head), 4)
        info.is_executable = os.access(path, os.X_OK)
        if info.entropy > 7.5:
            info.notes.append("high entropy - packed/encrypted")
        if info.magic in ("ELF", "PE/DOS", "Mach-O 64"):
            info.is_executable = True
            info.notes.append("binary executable")
        return info

    @staticmethod
    def hex_dump(path, offset=0, length=256):
        data = Path(path).read_bytes()[offset:offset+length]
        lines = []
        for i in range(0, len(data), 16):
            chunk = data[i:i+16]
            hexp = " ".join(f"{b:02x}" for b in chunk)
            ascp = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
            lines.append(f"{offset+i:08x}  {hexp:<48}  {ascp}")
        return "\n".join(lines)
