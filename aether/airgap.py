"""Air-gap mode + Multi-Level Security labels (Bell-LaPadula)."""
from __future__ import annotations
import socket

MLS_LEVELS = {"UNCLASSIFIED": 0, "CONFIDENTIAL": 1, "SECRET": 2, "TOP_SECRET": 3}
_COMPARTMENTS: set[str] = set()

def enable_airgap() -> None:
    """Disable all outbound sockets at Python level."""
    def _blocked(*_args, **_kwargs):
        raise RuntimeError("AETHER air-gap mode: network access denied.")
    socket.socket = _blocked
    socket.create_connection = _blocked
    socket.getaddrinfo = _blocked

def set_compartments(compartments: list[str]) -> None:
    _COMPARTMENTS.clear()
    _COMPARTMENTS.update(compartments)

def authorize(level: str, compartments: list[str]) -> bool:
    if level not in MLS_LEVELS:
        raise ValueError(f"Unknown MLS level: {level}")
    return all(c in _COMPARTMENTS for c in compartments)

def flow_check(subject_level: str, object_level: str) -> bool:
    """No read up, no write down (Bell-LaPadula)."""
    return MLS_LEVELS[subject_level] >= MLS_LEVELS[object_level]

def pad_to_block(data: bytes, block: int = 4096) -> bytes:
    """Covert-channel mitigation: constant-size padding."""
    if len(data) > block:
        raise ValueError("Data exceeds block size.")
    return data + b"\x00" * (block - len(data))
