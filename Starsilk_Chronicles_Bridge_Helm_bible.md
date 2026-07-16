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
- Added committed optimized PNG art pack under `assets/bridge_helm`
- Included built-in QA commands for GUI smoke, gameplay, assets, accessibility, persistence, performance, balance, static sweep, and exhaustive bug sweep

### Mechanics

The project now implements a route-planning exploration loop with scan, focus, plot, travel, salvage, archive pulse, inspect, undo, reset, subsystem damage, final trial resolution, run memory, explicit crew assignment, explicit power reassignment, emergency actions, and node/route storylets with distinct consequences.

Crew roles are assigned to stations:

- Navigator at helm improves route danger handling.
- Engineer at engine improves fuel efficiency.
- Archivist at archive improves scan clarity and relic recovery chance.
- Medic at repair can stabilize damaged systems during salvage.

Power can be routed to helm, engine, or archive. The powered station gains stronger effects until power is reassigned.

Emergency actions are implemented:

- Brace: spends silk to repair hull while stressing crew.
- Vent: spends silk to reduce danger while stressing archive.
- Reroute: spends silk and engine integrity to recover fuel.

Storylets are implemented at route and node level. Route events create distinct travel consequences, while node storylets resolve through the current story posture: steady, bold, or merciful.

### Asset note

The repository now includes a compact committed PNG art pack:

- 8 node visuals
- 5 relic icons
- 4 system-status icons
- 3 route-state assets
- 3 ending-state assets
- manifest: `assets/bridge_helm/manifest.json`

Runtime placeholder generation remains as a fallback only when committed art assets are missing.

### Validation commands

```bash
python3 -m py_compile starsilk-chronicles-final.py bridge-helm-launcher.py tools/generate_bridge_assets.py
python3 tools/generate_bridge_assets.py
python3 bridge-helm-launcher.py --bug-sweep
```

### Known limitations

- Human playtesting remains unverified.
- Tkinter GUI is functional but not final production visual polish.
- The art pack is compact committed production-slice art, not final commissioned art.
- Audio cues are still absent.

### Do-not-touch warnings

- Do not reintroduce prompt-production queue UI into the game engine.
- Do not replace Bridge Helm state with an unrelated parallel state model.
- Do not force-push or rewrite history.

### Remaining work

1. Polish GUI layout and information hierarchy now that crew, power, emergencies, and story posture all exist.
2. Add audio cues for scan, plot, travel, salvage, emergency actions, damage, relic recovery, and final trial.
3. Expand storylet count and add more multi-step consequences for repeat play.
4. Human-playtest balance and dominant strategies after the mechanics pass.
5. Replace compact generated-style art with final commissioned art when art direction is locked.

### Commit record

- Seed commit: `dd386cac0198c0cee955258c9887c1aa70f799ea`
- Asset-generator fix: `ffd00f71542bcbf348fcaeb66f169efcf1325406`
- Dynamic route-control fix: `7835b3222dbcf3e771516017a28273006be97b0c`
