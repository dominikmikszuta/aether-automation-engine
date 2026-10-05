"""EMBER - Stack-based bytecode VM with assembler and disassembler."""
from __future__ import annotations
from dataclasses import dataclass


OPCODES = {
    "PUSH": 0x01, "POP": 0x02, "DUP": 0x03, "SWAP": 0x04,
    "ADD": 0x10, "SUB": 0x11, "MUL": 0x12, "DIV": 0x13,
    "MOD": 0x14, "NEG": 0x15, "CMP": 0x16,
    "JMP": 0x20, "JZ": 0x21, "JNZ": 0x22,
    "LOAD": 0x30, "STORE": 0x31,
    "CALL": 0x40, "RET": 0x41,
    "PRINT": 0x50, "HALT": 0xFF,
}


@dataclass
class Instruction:
    op: str
    arg: int = 0

    def encode(self):
        return bytes([OPCODES[self.op]]) + self.arg.to_bytes(4, "little")

    def __repr__(self):
        return f"{self.op} {self.arg}" if self.arg else self.op


class Assembler:
    @staticmethod
    def parse(text):
        instructions = []
        labels = {}
        lines = []
        for line in text.splitlines():
            line = line.split(";")[0].strip()
            if not line:
                continue
            if line.endswith(":"):
                labels[line[:-1]] = len(lines)
                continue
            lines.append(line)

        for line in lines:
            parts = line.split(None, 1)
            op = parts[0].upper()
            arg = 0
            if len(parts) > 1:
                val = parts[1].strip()
                if val in labels:
                    arg = labels[val]
                else:
                    try:
                        arg = int(val, 0)
                    except ValueError:
                        arg = 0
            if op in OPCODES:
                instructions.append(Instruction(op, arg))
        return instructions


class VM:
    def __init__(self):
        self.stack = []
        self.vars = {}
        self.pc = 0
        self.output = []
        self.halted = False

    def _pop(self):
        if not self.stack:
            raise RuntimeError("stack underflow")
        return self.stack.pop()

    def _push(self, v):
        self.stack.append(v)

    def step(self, program):
        if self.pc >= len(program) or self.halted:
            return False
        ins = program[self.pc]
        self.pc += 1
        op = ins.op

        if op == "PUSH": self._push(ins.arg)
        elif op == "POP": self._pop()
        elif op == "DUP": self._push(self.stack[-1])
        elif op == "SWAP":
            a, b = self._pop(), self._pop()
            self._push(a); self._push(b)
        elif op == "ADD": b, a = self._pop(), self._pop(); self._push(a + b)
        elif op == "SUB": b, a = self._pop(), self._pop(); self._push(a - b)
        elif op == "MUL": b, a = self._pop(), self._pop(); self._push(a * b)
        elif op == "DIV": b, a = self._pop(), self._pop(); self._push(a // b if b else 0)
        elif op == "MOD": b, a = self._pop(), self._pop(); self._push(a % b if b else 0)
        elif op == "NEG": self._push(-self._pop())
        elif op == "CMP":
            b, a = self._pop(), self._pop()
            self._push(1 if a > b else (-1 if a < b else 0))
        elif op == "JMP": self.pc = ins.arg
        elif op == "JZ":
            if self._pop() == 0: self.pc = ins.arg
        elif op == "JNZ":
            if self._pop() != 0: self.pc = ins.arg
        elif op == "LOAD": self._push(self.vars.get(ins.arg, 0))
        elif op == "STORE": self.vars[ins.arg] = self._pop()
        elif op == "PRINT": self.output.append(self._pop())
        elif op == "HALT": self.halted = True
        return True

    def run(self, program, max_steps=100000):
        steps = 0
        while self.step(program) and steps < max_steps:
            steps += 1
        return self.output


class Disassembler:
    @staticmethod
    def disasm(program):
        lines = []
        for i, ins in enumerate(program):
            lines.append(f"{i:04d}  {ins!r}")
        return "\n".join(lines)
