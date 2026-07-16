#!/usr/bin/env python3
"""Build deterministic Bridge Helm production-slice art and audio assets."""
from __future__ import annotations

import json
import math
import base64
import struct
import wave
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "assets" / "bridge_helm"
AUDIO_DIR = ROOT / "audio" / "bridge_helm"

NODES = {
    "wake": ("Starwake Berth", "#5bd3ff", "dock"),
    "ledger_gate": ("Ledger Gate", "#b783ff", "gate"),
    "witness_pool": ("Witness Pool", "#73e0d4", "pool"),
    "moth_orchard": ("Moth Orchard", "#ffd166", "orchard"),
    "ashen_comet": ("Ashen Comet", "#ff8f66", "comet"),
    "red_archive": ("Red Archive", "#ff5d73", "archive"),
    "silkforge": ("Silkforge", "#ffd98a", "forge"),
    "last_lighthouse": ("Last Lighthouse", "#fff0ba", "lighthouse"),
}
RELICS = {
    "silkglass_compass": "#7fffd4",
    "archive_red_key": "#ff5d73",
    "lantern_moth_cocoon": "#ffd166",
    "ash_hymn_cylinder": "#ff8f66",
    "lighthouse_wick": "#fff0ba",
}
SYSTEMS = {
    "hull": "#7fffd4",
    "engine": "#ff8f66",
    "archive": "#b783ff",
    "crew": "#f2d28b",
}
ENDINGS = {
    "radiant": "#fff0ba",
    "fractured": "#9fb7ff",
    "lost": "#ff5d73",
}
AUDIO = {
    "scan": 660,
    "plot": 520,
    "travel": 390,
    "salvage": 470,
    "emergency": 180,
    "damage": 130,
    "relic": 740,
    "final": 880,
}


def write_payload(source: Path, chunk_size: int = 12000) -> None:
    payload_dir = source.with_suffix("")
    payload_dir.mkdir(parents=True, exist_ok=True)
    for old in payload_dir.glob("part_*.dat"):
        old.unlink()
    encoded = base64.b64encode(source.read_bytes()).decode("ascii")
    for index, start in enumerate(range(0, len(encoded), chunk_size)):
        (payload_dir / f"part_{index:02d}.dat").write_text(encoded[start : start + chunk_size], encoding="ascii")


def write_pack_archives() -> None:
    art_pack = ASSET_DIR / "bridge_helm_art_pack.zip"
    with zipfile.ZipFile(art_pack, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(ASSET_DIR.glob("**/*.png")) + [ASSET_DIR / "manifest.json"]:
            archive.write(path, path.relative_to(ASSET_DIR))
    write_payload(art_pack)

    audio_pack = AUDIO_DIR / "bridge_helm_audio_pack.zip"
    with zipfile.ZipFile(audio_pack, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(AUDIO_DIR.glob("*.wav")):
            archive.write(path, path.relative_to(AUDIO_DIR))
    write_payload(audio_pack)


def hex_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def save_png(img: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    img = img.convert("P", palette=Image.Palette.ADAPTIVE, colors=96)
    img.save(path, optimize=True)


def background(size: tuple[int, int], accent: str) -> Image.Image:
    w, h = size
    base = Image.new("RGB", size, "#081019")
    px = base.load()
    ar, ag, ab = hex_rgb(accent)
    for y in range(h):
        for x in range(w):
            glow = int(34 * (1 - y / h) + 20 * math.sin((x + y) / 42))
            px[x, y] = (
                min(255, 8 + glow + ar // 12),
                min(255, 16 + glow // 2 + ag // 14),
                min(255, 25 + glow + ab // 10),
            )
    return base.filter(ImageFilter.GaussianBlur(0.4))


def draw_node(name: str, label: str, accent: str, motif: str) -> None:
    img = background((160, 90), accent)
    d = ImageDraw.Draw(img)
    color = hex_rgb(accent)
    for i in range(10):
        x = (i * 23 + len(name) * 7) % 160
        y = (i * 17 + len(label) * 5) % 60
        d.point((x, y), fill=(220, 235, 240))
    d.line((10, 72, 150, 66), fill=color, width=2)
    d.line((14, 76, 146, 73), fill=(242, 210, 139), width=1)
    if motif == "dock":
        d.rectangle((26, 41, 134, 58), outline=color, width=2)
        d.arc((40, 21, 120, 80), 190, 350, fill=(242, 210, 139), width=2)
    elif motif == "gate":
        d.rounded_rectangle((53, 19, 107, 70), radius=4, outline=color, width=3)
        d.line((80, 21, 80, 69), fill=(242, 210, 139), width=1)
    elif motif == "pool":
        d.ellipse((41, 34, 119, 69), outline=color, width=3)
        d.arc((52, 41, 108, 64), 0, 180, fill=(242, 210, 139), width=1)
    elif motif == "orchard":
        for x in (48, 75, 102):
            d.line((x, 66, x + 6, 27), fill=(82, 61, 49), width=4)
            d.ellipse((x - 13, 19, x + 21, 47), outline=color, width=2)
    elif motif == "comet":
        d.ellipse((96, 30, 121, 55), fill=color)
        for off in range(3):
            d.line((96, 42 + off * 3, 21, 25 + off * 8), fill=(255, 185, 140), width=1)
    elif motif == "archive":
        for x in range(41, 119, 13):
            d.rectangle((x, 24, x + 6, 69), outline=color, width=1)
        d.rectangle((37, 69, 123, 73), fill=(242, 210, 139))
    elif motif == "forge":
        d.polygon((39, 66, 80, 24, 121, 66), outline=color)
        d.arc((52, 28, 108, 84), 200, 340, fill=(242, 210, 139), width=3)
    else:
        d.rectangle((75, 21, 85, 68), fill=color)
        d.polygon((80, 10, 58, 41, 102, 41), outline=(242, 210, 139))
        d.ellipse((73, 11, 87, 25), fill=(255, 242, 190))
    d.text((8, 76), label[:24], fill=(235, 244, 248))
    save_png(img, ASSET_DIR / "nodes" / f"{name}.png")


def draw_icon(path: Path, accent: str, kind: str) -> None:
    img = Image.new("RGBA", (64, 64), (8, 16, 25, 255))
    d = ImageDraw.Draw(img)
    c = hex_rgb(accent)
    d.rounded_rectangle((5, 5, 59, 59), radius=12, outline=c, width=3)
    if kind == "key":
        d.ellipse((16, 23, 31, 38), outline=c, width=5)
        d.line((30, 30, 51, 30), fill=c, width=5)
        d.line((44, 30, 44, 39), fill=c, width=4)
    elif kind == "compass":
        d.ellipse((15, 15, 49, 49), outline=c, width=4)
        d.polygon((32, 17, 39, 36, 32, 47, 25, 36), fill=c)
    elif kind == "cocoon":
        d.ellipse((20, 12, 44, 52), outline=c, width=5)
        for y in range(20, 47, 8):
            d.arc((18, y - 12, 46, y + 12), 0, 180, fill=(242, 210, 139), width=2)
    elif kind == "cylinder":
        d.rectangle((19, 17, 45, 47), outline=c, width=4)
        d.ellipse((19, 12, 45, 23), outline=c, width=4)
        d.ellipse((19, 41, 45, 52), outline=c, width=4)
    elif kind == "wick":
        d.line((32, 47, 32, 19), fill=c, width=6)
        d.ellipse((23, 12, 41, 31), fill=(255, 242, 190))
    else:
        d.polygon((32, 11, 52, 52, 12, 52), outline=c, width=5)
    save_png(img, path)


def build_assets() -> None:
    for name, (label, accent, motif) in NODES.items():
        draw_node(name, label, accent, motif)
    relic_kind = {
        "silkglass_compass": "compass",
        "archive_red_key": "key",
        "lantern_moth_cocoon": "cocoon",
        "ash_hymn_cylinder": "cylinder",
        "lighthouse_wick": "wick",
    }
    for name, accent in RELICS.items():
        draw_icon(ASSET_DIR / "relics" / f"{name}.png", accent, relic_kind[name])
    for name, accent in SYSTEMS.items():
        draw_icon(ASSET_DIR / "systems" / f"{name}.png", accent, name)
        for state, alpha in {"warning": 160, "critical": 220, "recovered": 120}.items():
            img = Image.open(ASSET_DIR / "systems" / f"{name}.png").convert("RGBA")
            d = ImageDraw.Draw(img)
            d.rectangle((4, 48, 60, 59), fill=(255, 111, 97, alpha) if state != "recovered" else (127, 255, 212, alpha))
            d.text((8, 49), state.upper()[:8], fill=(8, 16, 25))
            save_png(img, ASSET_DIR / "systems" / f"{name}_{state}.png")
    for route, accent in {"available": "#7fffd4", "plotted": "#ffd166", "blocked": "#ff5d73"}.items():
        img = background((96, 36), accent)
        d = ImageDraw.Draw(img)
        c = hex_rgb(accent)
        d.line((8, 18, 88, 18), fill=c, width=5)
        d.ellipse((6, 13, 15, 22), fill=c)
        d.ellipse((80, 10, 93, 26), outline=c, width=3)
        d.text((20, 6), route.upper(), fill=(235, 244, 248))
        save_png(img, ASSET_DIR / "routes" / f"{route}.png")
    for ending, accent in ENDINGS.items():
        img = background((160, 90), accent)
        d = ImageDraw.Draw(img)
        c = hex_rgb(accent)
        d.polygon((80, 11, 110, 72, 50, 72), outline=c, width=5)
        d.ellipse((69, 24, 91, 46), fill=c)
        d.text((9, 75), ending.upper(), fill=(235, 244, 248))
        save_png(img, ASSET_DIR / "endings" / f"{ending}.png")
    manifest = {
        "generated": False,
        "style": "production-slice storybook star-map PNG art pack",
        "version": "1.4.0-production-slice-alpha",
        "assets": sorted(str(path.relative_to(ASSET_DIR)) for path in ASSET_DIR.glob("**/*.png")),
    }
    (ASSET_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def build_audio() -> None:
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    sample_rate = 8000
    for cue, freq in AUDIO.items():
        frames = []
        duration = 0.08 if cue not in {"emergency", "final"} else 0.12
        count = int(sample_rate * duration)
        for i in range(count):
            t = i / sample_rate
            env = 1 - i / count
            tone = math.sin(2 * math.pi * freq * t) + 0.35 * math.sin(2 * math.pi * (freq * 1.5) * t)
            frames.append(struct.pack("<h", int(13000 * env * tone)))
        with wave.open(str(AUDIO_DIR / f"{cue}.wav"), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)
            wav.writeframes(b"".join(frames))


def main() -> int:
    build_assets()
    build_audio()
    write_pack_archives()
    print("Bridge Helm production-slice assets and pack payloads rebuilt.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
