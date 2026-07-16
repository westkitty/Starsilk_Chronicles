# Starsilk Chronicles: Bridge Helm

A local-first Python/Tkinter tactical exploration alpha for **Starsilk Chronicles**.

The Bridge Helm loop is:

```text
scan sector -> assign crew/power -> inspect route previews -> choose story posture -> plot a course -> commit travel -> salvage or trigger emergencies -> resolve event chains -> survive the final explanation
```

## Run

```bash
python3 bridge-helm-launcher.py --gui
```

## Validate

```bash
python3 -m py_compile starsilk-chronicles-final.py bridge-helm-launcher.py tools/generate_bridge_assets.py
python3 tools/build_production_assets.py
python3 tools/generate_bridge_assets.py
python3 bridge-helm-launcher.py --bug-sweep
```

## Other checks

```bash
python3 bridge-helm-launcher.py --gui-smoke
python3 bridge-helm-launcher.py --gui-qa
python3 bridge-helm-launcher.py --gameplay-qa
python3 bridge-helm-launcher.py --asset-qa
python3 bridge-helm-launcher.py --accessibility-qa
python3 bridge-helm-launcher.py --persistence-qa
python3 bridge-helm-launcher.py --performance-qa
python3 bridge-helm-launcher.py --balance-sim
```

## Current delivery note

The repository now includes committed production-slice pack payloads under `assets/bridge_helm/bridge_helm_art_pack/` and `audio/bridge_helm/bridge_helm_audio_pack/`. The runtime reconstructs and extracts eight node scenes, five relic icons, system icons with state variants, route-state assets, ending splashes, and audio cues from those payloads when needed. Runtime placeholder generation remains as a fallback only when committed packs are missing.
