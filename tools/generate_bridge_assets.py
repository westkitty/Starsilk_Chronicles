#!/usr/bin/env python3
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "starsilk-chronicles-final.py"
spec = importlib.util.spec_from_file_location("bridge_engine", ENGINE)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)
module.ensure_placeholder_assets()
print("Generated Bridge Helm placeholder runtime assets.")
