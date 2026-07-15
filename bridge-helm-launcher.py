#!/usr/bin/env python3
"""Launcher wrapper for Starsilk Chronicles: Bridge Helm."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
ENGINE = ROOT / "starsilk-chronicles-final.py"


def load_engine():
    spec = importlib.util.spec_from_file_location("starsilk_chronicles_bridge", ENGINE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load engine at {ENGINE}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main(argv=None) -> int:
    module = load_engine()
    return int(module.main(argv))

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
