# Starsilk Chronicles: Bridge Helm

A local-first Python/Tkinter tactical exploration alpha for **Starsilk Chronicles**.

The Bridge Helm loop is:

```text
scan sector -> inspect route previews -> plot a course -> commit travel -> salvage/repair -> survive the final explanation
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

This repository was populated through the GitHub connector after the local `/mnt/data` environment could not perform a normal network `git push`. The large generated PNG art package is not committed here; the engine can create tiny placeholder runtime PNGs during asset QA so the repository remains runnable and testable.
