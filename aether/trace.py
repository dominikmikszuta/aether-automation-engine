"""TRACE - XOR bruteforce and scoring."""
from __future__ import annotations
from pathlib import Path

class Trace:
    FREQ = {"e":12.7,"t":9.1,"a":8.2,"o":7.5,"i":7.0,"n":6.7,"s":6.3,
            "h":6.1,"r":6.0,"d":4.3,"l":4.0,"c":2.8,"u":2.8,"m":2.4,
            "w":2.4,"f":2.2,"g":2.0,"y":2.0,"p":1.9,"b":1.5,"v":1.0,
            " ":18.0}

    @classmethod
    def score(cls, text):
        if not text: return 0.0
        t = text.lower()
        return sum(cls.FREQ.get(c, 0.0) for c in t) / len(t)

    @staticmethod
    def xor_single(data, key):
        return bytes(b ^ key for b in data)

    @classmethod
    def bruteforce_single(cls, data, top=10):
        results = []
        for key in range(256):
            dec = cls.xor_single(data, key)
            try:
                text = dec.decode("ascii", "ignore")
                s = cls.score(text)
                if s > 0:
                    results.append({"key": key, "key_hex": f"0x{key:02x}",
                                    "score": round(s, 3), "preview": text[:80]})
            except Exception: pass
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top]
