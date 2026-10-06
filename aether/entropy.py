"""ENTROPY - Shannon entropy analyzer."""
from __future__ import annotations
from math import log2
from pathlib import Path

class EntropyAnalyzer:
    @staticmethod
    def shannon(data):
        if not data: return 0.0
        freq = [0] * 256
        for b in data: freq[b] += 1
        n = len(data)
        return -sum((c/n) * log2(c/n) for c in freq if c)

    def block_analysis(self, path, block_size=4096):
        data = Path(path).read_bytes()
        return [
            {"offset": i, "size": len(data[i:i+block_size]),
             "entropy": round(self.shannon(data[i:i+block_size]), 4)}
            for i in range(0, len(data), block_size)
        ]

    def classify(self, e):
        if e < 1.0: return "constant"
        if e < 3.0: return "plaintext"
        if e < 5.0: return "code"
        if e < 7.0: return "mixed"
        if e < 7.9: return "compressed/encrypted"
        return "random/packed"

    def summary(self, path, block_size=4096):
        blocks = self.block_analysis(path, block_size)
        avg = sum(b["entropy"] for b in blocks) / len(blocks) if blocks else 0.0
        return {
            "file": str(path), "blocks": len(blocks),
            "avg_entropy": round(avg, 4),
            "max_entropy": round(max((b["entropy"] for b in blocks), default=0), 4),
            "min_entropy": round(min((b["entropy"] for b in blocks), default=0), 4),
            "classification": self.classify(avg),
        }
