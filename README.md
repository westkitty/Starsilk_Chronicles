# Starsilk Chronicles: Bridge Helm

A local-first Python/Tkinter tactical exploration alpha for **Starsilk Chronicles**.

The Bridge Helm loop is:

```text
scan sector -> assign crew/power -> inspect route previews -> choose story posture -> plot a course -> commit travel -> salvage or trigger emergencies -> survive the final explanation
```

## Run

```bash
python3 bridge-helm-launcher.py --gui
```

## Validate

```bash
python3 -m py_compile starsilk-chronicles-final.py bridge-helm-launcher.py tools/generate_bridge_assets.py
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

The repository now includes a compact committed PNG art pack under `assets/bridge_helm`: eight node visuals, five relic icons, four system icons, three route-state assets, three ending-state assets, and a manifest. Runtime placeholder generation remains as a fallback only when committed assets are missing.
