# Starsilk Chronicles Bridge Helm Bible

## 2026-07-15 - GitHub repository delivery pass

Repository: `westkitty/Starsilk_Chronicles`
Branch: `main`

### Starting state

The GitHub repository existed but was empty. A seed commit was created first to initialize `main`.

### Goals

Deliver a runnable Bridge Helm project through GitHub despite the container lacking outbound Git network access.

### Implemented

- Added compact Bridge Helm engine: `starsilk-chronicles-final.py`
- Added launcher: `bridge-helm-launcher.py`
- Added README with run and validation commands
- Added additive project Bible
- Added `.gitignore`
- Added placeholder runtime asset generator: `tools/generate_bridge_assets.py`
- Included built-in QA commands for GUI smoke, gameplay, assets, accessibility, persistence, performance, balance, static sweep, and exhaustive bug sweep

### Mechanics

The project currently implements a route-planning exploration loop with scan, focus, plot, travel, salvage, archive pulse, inspect, undo, reset, subsystem damage, final trial resolution, and run memory. The Tkinter GUI now exposes dynamically reachable route plotting controls instead of a single hardcoded first route.

The code includes state fields for crew and power, but explicit crew assignment, power reassignment, emergency-action interfaces, contradiction-key mechanics, and black-box recap presentation are not implemented yet. Those are production targets, not completed mechanics.

### Asset note

The large PNG art package from the ChatGPT delivery environment was not committed by the connector because the available GitHub tool cannot stage local binary trees. The repository engine can generate placeholder PNG runtime files through `tools/generate_bridge_assets.py` or during `--asset-qa`; those generated files are ignored by Git.

### Validation commands

```bash
python3 -m py_compile starsilk-chronicles-final.py bridge-helm-launcher.py tools/generate_bridge_assets.py
python3 tools/generate_bridge_assets.py
python3 bridge-helm-launcher.py --bug-sweep
```

### Known limitations

- The committed repo uses placeholder-generated asset files rather than the full 68 MB local art package.
- Explicit crew assignment, power tradeoffs, emergency actions, contradiction-key play, and black-box recap presentation remain unimplemented.
- Human playtesting remains unverified.
- Tkinter GUI is functional but not final production visual polish.

### Do-not-touch warnings

- Do not reintroduce prompt-production queue UI into the game engine.
- Do not replace Bridge Helm state with an unrelated parallel state model.
- Do not force-push or rewrite history.

### Remaining work

1. Replace placeholder-generated assets with a real optimized art pack for the eight chart locations, route lines, relic icons, system-status icons, and ending states.
2. Implement explicit crew assignment, power reassignment, and emergency actions so the existing crew and power state fields become meaningful player decisions.
3. Expand authored route storylets and event chains so each node has distinct choices, consequences, and replay texture.
4. Add richer visible animation, sound cues, readable map states, and more polished status surfaces.
5. Human-playtest balance and dominant strategies after the mechanics pass.

### Commit record

- Seed commit: `dd386cac0198c0cee955258c9887c1aa70f799ea`
- Asset-generator fix: `ffd00f71542bcbf348fcaeb66f169efcf1325406`
- Dynamic route-control fix: `7835b3222dbcf3e771516017a28273006be97b0c`
