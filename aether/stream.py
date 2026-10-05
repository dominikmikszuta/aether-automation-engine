"""STREAM - Network protocols: HTTP, DNS, WebSocket frame parser."""
from __future__ import annotations
import json, socket, struct, urllib.request
from dataclasses import dataclass


@dataclass
class HTTPResponse:
    status: int
    headers: dict
    body: bytes
    elapsed_ms: float = 0.0


class HTTP:
    @staticmethod
    def get(url, timeout=10, headers=None):
        import time
        req = urllib.request.Request(url, headers=headers or {})
        start = time.perf_counter()
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return HTTPResponse(
                status=r.status,
                headers=dict(r.headers),
                body=r.read(),
                elapsed_ms=(time.perf_counter() - start) * 1000,
            )

    @staticmethod
    def post(url, data=None, json_data=None, timeout=10, headers=None):
        import time
        hdrs = dict(headers or {})
        body = b""
        if json_data is not None:
            body = json.dumps(json_data).encode()
            hdrs["Content-Type"] = "application/json"
        elif data is not None:
            body = data if isinstance(data, bytes) else data.encode()
        req = urllib.request.Request(url, data=body, headers=hdrs, method="POST")
        start = time.perf_counter()
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return HTTPResponse(
                status=r.status,
                headers=dict(r.headers),
                body=r.read(),
                elapsed_ms=(time.perf_counter() - start) * 1000,
            )


class DNS:
    @staticmethod
    def resolve(host, timeout=5):
        try:
            _, _, ips = socket.gethostbyname_ex(host)
            return ips
        except socket.gaierror as e:
            return [f"error: {e}"]

    @staticmethod
    def reverse(ip):
        try:
            return socket.gethostbyaddr(ip)[0]
        except socket.herror:
            return None


class WebSocketFrame:
    OPCODES = {0x0: "continue", 0x1: "text", 0x2: "binary",
                0x8: "close", 0x9: "ping", 0xA: "pong"}

    @staticmethod
    def parse(data: bytes):
        if len(data) < 2:
            return None
        b1, b2 = data[0], data[1]
        fin = (b1 >> 7) & 1
        opcode = b1 & 0x0F
        masked = (b2 >> 7) & 1
        length = b2 & 0x7F
        offset = 2
        if length == 126:
            length = struct.unpack(">H", data[2:4])[0]; offset = 4
        elif length == 127:
            length = struct.unpack(">Q", data[2:10])[0]; offset = 10
        mask_key = b""
        if masked:
            mask_key = data[offset:offset + 4]; offset += 4
        payload = data[offset:offset + length]
        if masked:
            payload = bytes(b ^ mask_key[i % 4] for i, b in enumerate(payload))
        return {
            "fin": bool(fin), "opcode": WebSocketFrame.OPCODES.get(opcode, hex(opcode)),
            "masked": bool(masked), "length": length, "payload": payload,
        }

    @staticmethod
    def encode(payload, opcode=0x1, mask=False):
        if isinstance(payload, str):
            payload = payload.encode()
        b1 = 0x80 | opcode
        length = len(payload)
        if length < 126:
            header = bytes([b1, length])
        elif length < 65536:
            header = bytes([b1, 126]) + struct.pack(">H", length)
        else:
            header = bytes([b1, 127]) + struct.pack(">Q", length)
        return header + payload
