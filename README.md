# NTCIP Traffic Controller Simulator

Browser-based simulation of a NEMA dual-ring 8-phase traffic signal controller with a live NTCIP 1202 MIB OID viewer.

**Live demo:** https://d1r8pxnmau5sot.cloudfront.net

## Overview

This tool simulates the timing logic of a real-world NEMA dual-ring traffic signal controller — the same type deployed at signalized intersections across the US. It runs entirely in the browser with no server or API calls. The NTCIP Objects tab displays real SNMP OID paths from the NTCIP 1202 standard, with values that update live as the simulation runs, giving ITS engineers and students a hands-on look at how a traffic management center queries a physical controller.

## Features

- **Canvas intersection visualization** — 440×440px animated intersection showing active signal heads per approach, updated each simulation tick
- **Four-tab control panel:**
  - *Timing Plan* — adjust cycle length (60–180s), yellow clearance (2–6s), per-phase split percentages, and simulation speed (1–10×); cycle progress bar with live cursor
  - *Ring/Barrier* — visual dual-ring diagram showing Φ1–Φ8 with active/yellow states and live countdown timers; barrier markers at ring sync points
  - *NTCIP Objects* — live NTCIP 1202 MIB OIDs across four collapsible groups: Controller Status, Phase Status (phaseGreen/phaseYellow per phase), Phase Timing Parameters, Unit Status
  - *Learn NTCIP* — five reference cards covering NTCIP/SNMP basics, dual-ring architecture, timing plans, OID structure, and the NTCIP standards stack
- **Five timing presets** — AM Peak, PM Peak, Off-Peak, Heavy Freight, Ped Priority
- **Concurrent phase pairs** — Φ1+Φ5 → Φ2+Φ6 ⟂ Φ3+Φ7 → Φ4+Φ8, with barrier enforcement
- **PWA** — installable, runs offline after first load via service worker cache
- **Mobile-responsive** — single-column layout on narrow viewports; tab bar scrolls on small screens

## Tech stack

| Layer | Technology |
|---|---|
| Markup / style / logic | Vanilla HTML5, CSS3, JavaScript |
| Intersection rendering | Canvas API |
| PWA | Service Worker + Web App Manifest |
| Hosting | AWS S3 + CloudFront |

No npm, no bundler, no framework, no external JS libraries.

## Architecture

The entire application is a single `index.html` file. Controller state (`cycleLen`, `yellowTime`, `simSpeed`, `cycleElapsed`, phase splits) is held in plain JS variables. A `setInterval` loop advances `cycleElapsed` each tick and determines the active phase pair based on cumulative split thresholds. The canvas, phase bar, ring diagram, and OID tree all read from the same state object and re-render on each tick. The service worker caches `index.html`, `manifest.json`, and the PWA icons at install time for offline use.

## Local development

```bash
# Open directly in a browser, or serve over HTTP
python3 -m http.server 8080
```

No build step, no dependencies to install.

## Deployment

Deployed manually to AWS S3 + CloudFront. There is no CI/CD workflow — sync by hand:

```bash
aws s3 sync . s3://jimmy-ntcip-simulator \
  --profile portfolio-user \
  --exclude ".git/*"
```

**S3 bucket:** `jimmy-ntcip-simulator` (us-east-1)

## Project structure

```
ntcip-simulator/
├── index.html      # Complete application — HTML, CSS, and JS in one file
├── manifest.json   # PWA manifest (name, icons, display mode)
├── sw.js           # Service worker — cache-first, cache key ntcip-sim-v2
└── icon-*.png      # PWA icons (192×192, 512×512, favicons)
```

## License

MIT — see [LICENSE](LICENSE)

## Author

Jimmy Hubbard — [github.com/jhubb88](https://github.com/jhubb88)

---

*Part of [jhubb88's portfolio](https://jimmyhubbard2.cc)*
