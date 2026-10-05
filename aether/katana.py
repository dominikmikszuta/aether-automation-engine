"""KATANA - Minimal regex engine with NFA matching."""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class State:
    is_end: bool = False
    transitions: dict = field(default_factory=dict)  # char -> set(state_id)
    epsilon: set = field(default_factory=set)       # state_ids
    any_char: set = field(default_factory=set)      # state_ids for '.'


class NFA:
    def __init__(self):
        self.states = {}
        self._next_id = 0
        self.start = None
        self.accept = None

    def new_state(self):
        sid = self._next_id
        self.states[sid] = State()
        self._next_id += 1
        return sid

    @staticmethod
    def _literal(pattern):
        n = NFA()
        start = n.new_state(); end = n.new_state()
        n.states[start].transitions[pattern] = {end}
        n.start = start; n.accept = end
        n.states[end].is_end = True
        return n

    @staticmethod
    def _any():
        n = NFA()
        s = n.new_state(); e = n.new_state()
        n.states[s].any_char = {e}
        n.start = s; n.accept = e
        n.states[e].is_end = True
        return n

    @staticmethod
    def concat(a, b):
        n = NFA()
        n.states = {**a.states, **{k + a._next_id: v for k, v in b.states.items()}}
        n._next_id = a._next_id + b._next_id
        # merge transitions
        for k, v in b.states.items():
            n.states[k + a._next_id] = v
        n.states[a.accept].epsilon.add(b.start + a._next_id)
        n.states[a.accept].is_end = False
        n.start = a.start
        n.accept = b.accept + a._next_id
        return n

    @staticmethod
    def star(a):
        n = NFA()
        s = n.new_state(); e = n.new_state()
        offset = 2
        n.states.update({k + offset: v for k, v in a.states.items()})
        n.states[s].epsilon.add(a.start + offset)
        n.states[a.accept + offset].epsilon.update({a.start + offset, e})
        n.states[s].epsilon.add(e)
        n.start = s; n.accept = e
        n.states[e].is_end = True
        return n

    @staticmethod
    def alt(a, b):
        n = NFA()
        s = n.new_state(); e = n.new_state()
        off_a = 2
        off_b = 2 + a._next_id
        n.states.update({k + off_a: v for k, v in a.states.items()})
        n.states.update({k + off_b: v for k, v in b.states.items()})
        n.states[s].epsilon.update({a.start + off_a, b.start + off_b})
        n.states[a.accept + off_a].epsilon.add(e)
        n.states[b.accept + off_b].epsilon.add(e)
        n.start = s; n.accept = e
        n.states[e].is_end = True
        return n


def _compile(pattern):
    """Parse simplified regex: literals, '.', '*', '|'."""
    def parse_expr(s, pos):
        left, pos = parse_concat(s, pos)
        while pos < len(s) and s[pos] == "|":
            right, pos = parse_concat(s, pos + 1)
            left = NFA.alt(left, right)
        return left, pos

    def parse_concat(s, pos):
        result = None
        while pos < len(s) and s[pos] not in ("|", ")"):
            atom, pos = parse_atom(s, pos)
            if atom is None:
                break
            result = atom if result is None else NFA.concat(result, atom)
        if result is None:
            n = NFA(); s0 = n.new_state(); n.start = s0; n.accept = s0; n.states[s0].is_end = True
            result = n
        return result, pos

    def parse_atom(s, pos):
        if pos >= len(s):
            return None, pos
        c = s[pos]
        if c == "(":
            inner, p = parse_expr(s, pos + 1)
            if p < len(s) and s[p] == ")":
                p += 1
            atom = inner
        elif c == ".":
            atom = NFA._any(); p = pos + 1
        else:
            atom = NFA._literal(c); p = pos + 1
        if p < len(s) and s[p] == "*":
            atom = NFA.star(atom); p += 1
        return atom, p

    nfa, _ = parse_expr(pattern, 0)
    return nfa


def _epsilon_closure(nfa, states):
    stack = list(states); closure = set(states)
    while stack:
        sid = stack.pop()
        state = nfa.states.get(sid)
        if not state: continue
        for nxt in state.epsilon:
            if nxt not in closure:
                closure.add(nxt); stack.append(nxt)
    return closure


class Katana:
    @staticmethod
    def compile(pattern):
        return _compile(pattern)

    @staticmethod
    def match(nfa, text):
        current = _epsilon_closure(nfa, {nfa.start})
        for ch in text:
            nxt = set()
            for sid in current:
                st = nfa.states[sid]
                for target_set in (st.transitions.get(ch, set()), st.any_char):
                    nxt.update(target_set)
            if not nxt:
                return False
            current = _epsilon_closure(nfa, nxt)
        return any(nfa.states[sid].is_end for sid in current)

    @staticmethod
    def search(pattern, text):
        nfa = Katana.compile(pattern)
        for i in range(len(text)):
            for j in range(i + 1, len(text) + 1):
                if Katana.match(nfa, text[i:j]):
                    return (i, j)
        return None
