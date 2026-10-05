"""CODEX - Compression codecs: RLE, Huffman, delta."""
from __future__ import annotations
import heapq
from collections import Counter
from dataclasses import dataclass


class RLE:
    @staticmethod
    def compress(data: bytes) -> bytes:
        if not data: return b""
        out = bytearray()
        i = 0
        while i < len(data):
            j = i + 1
            while j < len(data) and data[j] == data[i] and (j - i) < 255:
                j += 1
            out.append(j - i)
            out.append(data[i])
            i = j
        return bytes(out)

    @staticmethod
    def decompress(data: bytes) -> bytes:
        out = bytearray()
        for i in range(0, len(data), 2):
            count = data[i]; byte = data[i + 1]
            out.extend([byte] * count)
        return bytes(out)


@dataclass
class HuffNode:
    freq: int
    byte: int = -1
    left: object = None
    right: object = None
    def __lt__(self, other): return self.freq < other.freq


class Huffman:
    @staticmethod
    def _build_tree(data):
        freq = Counter(data)
        heap = [HuffNode(f, b) for b, f in freq.items()]
        heapq.heapify(heap)
        while len(heap) > 1:
            a = heapq.heappop(heap); b = heapq.heappop(heap)
            heapq.heappush(heap, HuffNode(a.freq + b.freq, left=a, right=b))
        return heap[0] if heap else None

    @staticmethod
    def _codes(node, prefix="", table=None):
        if table is None: table = {}
        if node is None: return table
        if node.byte >= 0: table[node.byte] = prefix or "0"
        else:
            Huffman._codes(node.left, prefix + "0", table)
            Huffman._codes(node.right, prefix + "1", table)
        return table

    @staticmethod
    def compress(data: bytes):
        if not data: return b"", {}
        tree = Huffman._build_tree(data)
        codes = Huffman._codes(tree)
        bits = "".join(codes[b] for b in data)
        pad = (8 - len(bits) % 8) % 8
        bits += "0" * pad
        out = bytearray([pad])
        for i in range(0, len(bits), 8):
            out.append(int(bits[i:i + 8], 2))
        return bytes(out), codes

    @staticmethod
    def decompress(data: bytes, codes: dict) -> bytes:
        if not data: return b""
        pad = data[0]
        bits = "".join(f"{b:08b}" for b in data[1:])
        if pad: bits = bits[:-pad]
        reverse = {v: k for k, v in codes.items()}
        out = bytearray()
        buf = ""
        for bit in bits:
            buf += bit
            if buf in reverse:
                out.append(reverse[buf]); buf = ""
        return bytes(out)


class Delta:
    @staticmethod
    def encode(data: bytes) -> bytes:
        if not data: return b""
        out = bytearray([data[0]])
        for i in range(1, len(data)):
            out.append((data[i] - data[i - 1]) % 256)
        return bytes(out)

    @staticmethod
    def decode(data: bytes) -> bytes:
        if not data: return b""
        out = bytearray([data[0]])
        for i in range(1, len(data)):
            out.append((out[-1] + data[i]) % 256)
        return bytes(out)
