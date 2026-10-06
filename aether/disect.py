"""DISECT - ELF/PE header parser."""
from __future__ import annotations
import struct
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class HeaderInfo:
    format: str
    arch: str = ""
    bits: int = 0
    endian: str = ""
    entry_point: int = 0
    notes: list = field(default_factory=list)

class Disect:
    @staticmethod
    def _read(p, off, size):
        with open(p, "rb") as f:
            f.seek(off); return f.read(size)

    @classmethod
    def parse_elf(cls, path):
        info = HeaderInfo(format="ELF")
        head = cls._read(path, 0, 64)
        if len(head) < 64:
            info.notes.append("truncated"); return info
        ei_class = head[4]; ei_data = head[5]
        info.bits = 64 if ei_class == 2 else 32
        info.endian = "little" if ei_data == 1 else "big"
        end = "<" if ei_data == 1 else ">"
        machine = struct.unpack(end + "H", head[18:20])[0]
        arch_map = {0x03:"x86",0x3e:"x86_64",0x28:"ARM",0xb7:"AArch64",
                    0x08:"MIPS",0x14:"PowerPC",0xf3:"RISC-V",0x16:"S390"}
        info.arch = arch_map.get(machine, f"unknown(0x{machine:x})")
        if info.bits == 64:
            info.entry_point = struct.unpack(end + "Q", head[24:32])[0]
        else:
            info.entry_point = struct.unpack(end + "I", head[24:28])[0]
        info.notes.append(f"entry: 0x{info.entry_point:x}")
        return info

    @classmethod
    def parse_pe(cls, path):
        info = HeaderInfo(format="PE")
        dos = cls._read(path, 0, 64)
        if len(dos) < 64: return info
        e_lfanew = struct.unpack("<I", dos[60:64])[0]
        head = cls._read(path, e_lfanew, 24)
        if head[:4] != b"PE\x00\x00":
            info.notes.append("invalid PE"); return info
        machine = struct.unpack("<H", head[4:6])[0]
        arch_map = {0x14c:"x86",0x8664:"x86_64",0x1c0:"ARM",0xaa64:"AArch64"}
        info.arch = arch_map.get(machine, f"unknown(0x{machine:x})")
        info.bits = 64 if machine in (0x8664, 0xaa64) else 32
        return info

    @classmethod
    def parse(cls, path):
        head = cls._read(path, 0, 4)
        if head.startswith(b"\x7fELF"): return cls.parse_elf(path)
        if head.startswith(b"MZ"): return cls.parse_pe(path)
        return HeaderInfo(format="unknown", notes=["not ELF/PE"])
