"""PACKET - TLV binary serialization with typed fields."""
from __future__ import annotations
import struct
from io import BytesIO


TYPE_NULL = 0x00
TYPE_BOOL = 0x01
TYPE_INT = 0x02
TYPE_FLOAT = 0x03
TYPE_STR = 0x04
TYPE_BYTES = 0x05
TYPE_LIST = 0x06
TYPE_DICT = 0x07


class Packet:
    @staticmethod
    def encode(value) -> bytes:
        buf = BytesIO()
        Packet._write(buf, value)
        return buf.getvalue()

    @staticmethod
    def _write(buf, value):
        if value is None:
            buf.write(bytes([TYPE_NULL]))
        elif isinstance(value, bool):
            buf.write(bytes([TYPE_BOOL, 1 if value else 0]))
        elif isinstance(value, int):
            buf.write(bytes([TYPE_INT])); buf.write(struct.pack(">q", value))
        elif isinstance(value, float):
            buf.write(bytes([TYPE_FLOAT])); buf.write(struct.pack(">d", value))
        elif isinstance(value, str):
            data = value.encode("utf-8")
            buf.write(bytes([TYPE_STR])); buf.write(struct.pack(">I", len(data))); buf.write(data)
        elif isinstance(value, (bytes, bytearray)):
            buf.write(bytes([TYPE_BYTES])); buf.write(struct.pack(">I", len(value))); buf.write(value)
        elif isinstance(value, (list, tuple)):
            buf.write(bytes([TYPE_LIST])); buf.write(struct.pack(">I", len(value)))
            for v in value: Packet._write(buf, v)
        elif isinstance(value, dict):
            buf.write(bytes([TYPE_DICT])); buf.write(struct.pack(">I", len(value)))
            for k, v in value.items():
                Packet._write(buf, k); Packet._write(buf, v)
        else:
            raise TypeError(f"Unsupported: {type(value).__name__}")

    @staticmethod
    def decode(data: bytes):
        buf = BytesIO(data)
        return Packet._read(buf)

    @staticmethod
    def _read(buf):
        t = buf.read(1)[0]
        if t == TYPE_NULL: return None
        if t == TYPE_BOOL: return bool(buf.read(1)[0])
        if t == TYPE_INT: return struct.unpack(">q", buf.read(8))[0]
        if t == TYPE_FLOAT: return struct.unpack(">d", buf.read(8))[0]
        if t == TYPE_STR:
            n = struct.unpack(">I", buf.read(4))[0]; return buf.read(n).decode("utf-8")
        if t == TYPE_BYTES:
            n = struct.unpack(">I", buf.read(4))[0]; return buf.read(n)
        if t == TYPE_LIST:
            n = struct.unpack(">I", buf.read(4))[0]
            return [Packet._read(buf) for _ in range(n)]
        if t == TYPE_DICT:
            n = struct.unpack(">I", buf.read(4))[0]
            return {Packet._read(buf): Packet._read(buf) for _ in range(n)}
        raise ValueError(f"Unknown type: {t}")
