import os, sys, tempfile
from pathlib import Path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from aether.pulse import Channel, Runtime
from aether.lynx import Lynx
from aether.ember import Assembler, VM, Disassembler
from aether.stream import WebSocketFrame, DNS
from aether.packet import Packet
from aether.codex import RLE, Huffman, Delta
from aether.halo import Halo
from aether.nest import Nest, Response
from aether.katana import Katana
from aether.oracle import Oracle


def test_pulse_channel():
    import asyncio
    async def run():
        c = Channel()
        await c.send(42)
        return await c.recv()
    assert asyncio.run(run()) == 42


def test_pulse_runtime():
    import asyncio
    async def run():
        r = Runtime()
        results = []
        async def handler(msg): results.append(msg)
        a = r.actor("t", handler)
        await a.inbox.send("hello")
        await asyncio.sleep(0.05)
        await r.stop_all()
        return results
    assert asyncio.run(run()) == ["hello"]


def test_lynx_load():
    with tempfile.TemporaryDirectory() as t:
        p = Path(t, "plug.py")
        p.write_text("def register(plugin):\n    plugin.register('boot', lambda: 'ok')\n")
        lx = Lynx(t)
        plugin = lx.load(p)
        assert plugin.name == "plug"
        assert lx.fire("boot")["plug"] == ["ok"]


def test_ember_arithmetic():
    src = """
        PUSH 5
        PUSH 3
        ADD
        PRINT
        HALT
    """
    program = Assembler.parse(src)
    vm = VM()
    output = vm.run(program)
    assert output == [8]


def test_ember_loop():
    # countdown via jnz: push 3, loop: dup, print, push 1, sub, dup, jnz loop
    src = """
        PUSH 3
    loop:
        DUP
        PRINT
        PUSH 1
        SUB
        DUP
        JNZ loop
        POP
        HALT
    """
    program = Assembler.parse(src)
    vm = VM()
    output = vm.run(program)
    assert 3 in output and 1 in output


def test_ember_disasm():
    program = Assembler.parse("PUSH 1\nPUSH 2\nADD\nHALT")
    text = Disassembler.disasm(program)
    assert "PUSH 1" in text


def test_stream_websocket_encode_parse():
    frame = WebSocketFrame.encode("hello", opcode=0x1)
    parsed = WebSocketFrame.parse(frame)
    assert parsed["payload"] == b"hello"
    assert parsed["opcode"] == "text"


def test_stream_dns_resolve_localhost():
    ips = DNS.resolve("localhost")
    assert any("127" in ip or "::" in ip for ip in ips)


def test_packet_roundtrip():
    original = {"a": 1, "b": [1, 2.5, "three"], "c": {"nested": True}, "d": None}
    encoded = Packet.encode(original)
    decoded = Packet.decode(encoded)
    assert decoded == original


def test_codex_rle():
    data = b"AAAABBBCCDAA"
    compressed = RLE.compress(data)
    assert RLE.decompress(compressed) == data


def test_codex_huffman():
    data = b"hello world hello world"
    compressed, codes = Huffman.compress(data)
    assert Huffman.decompress(compressed, codes) == data


def test_codex_delta():
    data = bytes([1, 2, 3, 5, 8, 13])
    assert Delta.decode(Delta.encode(data)) == data


def test_halo_bar():
    h = Halo()
    bar = h.bar(5, 10, width=10)
    assert "#####" in bar and "-----" in bar


def test_nest_route():
    app = Nest()
    @app.get("/hello/<name>")
    def hi(req):
        return Response(f"Hello {req.params['name']}")
    class FakeReq:
        def __init__(self):
            self.method = "GET"; self.path = "/hello/world"
            self.query = {}; self.headers = {}; self.body = b""; self.params = {}
    resp = app._dispatch(FakeReq())
    assert resp.body == "Hello world"


def test_katana_literal():
    nfa = Katana.compile("hello")
    assert Katana.match(nfa, "hello")
    assert not Katana.match(nfa, "world")


def test_katana_star():
    nfa = Katana.compile("ab*c")
    assert Katana.match(nfa, "ac")
    assert Katana.match(nfa, "abc")
    assert Katana.match(nfa, "abbbc")


def test_katana_alt():
    nfa = Katana.compile("cat|dog")
    assert Katana.match(nfa, "cat")
    assert Katana.match(nfa, "dog")
    assert not Katana.match(nfa, "bird")


def test_katana_any():
    nfa = Katana.compile("a.c")
    assert Katana.match(nfa, "abc")
    assert Katana.match(nfa, "axc")


def test_oracle_dag():
    o = Oracle()
    o.add("a", lambda: 1)
    o.add("b", lambda: 2)
    o.add("c", lambda a, b: a + b, deps=["a", "b"])
    results = o.run()
    assert results["c"] == 3


def test_oracle_cycle_detection():
    o = Oracle()
    o.add("a", lambda b: b, deps=["b"])
    o.add("b", lambda a: a, deps=["a"])
    try:
        o.run()
        assert False, "should have raised"
    except ValueError:
        pass


if __name__ == "__main__":
    for n, f in list(globals().items()):
        if n.startswith("test_") and callable(f):
            f()
    print("test_omega: PASS")
