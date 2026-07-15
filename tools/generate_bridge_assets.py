#!/usr/bin/env python3
"""Generate placeholder Bridge Helm runtime assets."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "starsilk-chronicles-final.py"
MODULE_NAME = "bridge_engine"


def load_engine():
    spec = importlib.util.spec_from_file_location(MODULE_NAME, ENGINE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load engine at {ENGINE}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    module = load_engine()
    module.ensure_placeholder_assets()
    print("Generated Bridge Helm placeholder runtime assets.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
