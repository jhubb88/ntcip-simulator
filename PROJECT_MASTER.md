# NTCIP Traffic Controller Simulator — Master Reference Document

*Operational reference + recruiter overview. Update when AWS resources change, after each phase, or when a key decision is revisited.*
*Last updated: 2026-05-14*

---

## 1. TL;DR

The NTCIP Traffic Controller Simulator encodes real-world NEMA dual-ring 8-phase traffic signal logic — the same controller type deployed at signalized intersections nationwide — into browser-side JavaScript, paired with a live NTCIP 1202 MIB OID viewer that shows how a Traffic Management Center queries a physical field controller via SNMP. The app provides four control panels for timing plan adjustment, ring/barrier visualization, OID inspection, and learning material, plus five preset timing plans (AM Peak, PM Peak, Off-Peak, Heavy Freight, Ped Priority). Stack: a single self-contained `index.html` (~48 KB) with inlined CSS and JS, no framework, no backend, PWA-installable, hosted on CloudFront + S3.

---

## 2. Live demo & repository

| Field | Value |
|---|---|
| Live URL | https://ntcip.jimmyhubbard2.cc (shorter subdomain than other portfolio projects — matches the protocol name) |
| Repository | https://github.com/jhubb88/ntcip-simulator |
| Status | Working end-to-end |
| Last deploy | 2026-05-08 (subdomain wiring; no content changes since 2026-04-21) |
| CI trigger | Push to `main` (S3 sync + CloudFront invalidation; no Lambda, no smoke test — there is no backend to test) |

---

## 3. Architecture

The entire application is a single `index.html` file with inlined CSS and JavaScript. Controller state (`cycleLen`, `yellowTime`, `simSpeed`, `cycleElapsed`, phase splits) lives in plain JS variables. A `setInterval` tick loop advances `cycleElapsed` each frame and determines the active phase pair based on cumulative split thresholds. The canvas, phase status bar, ring/barrier diagram, and NTCIP OID tree all read from the same state object and re-render on each tick. The service worker pre-caches `index.html`, `manifest.json`, and the PWA icons at install time; subsequent loads come from the local cache. No backend, no XHR or fetch at runtime, no third-party scripts.

### Stack

| Layer | Technology |
|---|---|
| Markup / style / logic | Vanilla HTML5, CSS3, JS (single `index.html`, ~1,200 lines, inlined styles + scripts) |
| Intersection rendering | Canvas API (`<canvas id="intersection">`, redraws each simulation tick) |
| Tick loop | `setInterval` driven by `simSpeed` (60-200 ms typical) |
| PWA | Service Worker (`sw.js`, cache-first, key `ntcip-sim-v2`) + Web App Manifest (`manifest.json`) |
| Hosting | S3 (`jimmy-ntcip-simulator`) + CloudFront (`E2PEIMT1J3W4MO`) |
| TLS | ACM cert, TLSv1.2_2021 minimum at CloudFront |
| CI/CD | GitHub Actions on push to `main` — S3 sync + CloudFront invalidation (32-line workflow, no Lambda step) |
| Helpers | `generate_icons.py` — one-time PWA icon generator, excluded from deploy sync |
| License | MIT |

### Data flow

```
First load:
┌─────────┐  GET /        ┌────────────┐  GET *     ┌──────────────────┐
│ Browser │ ─────────────►│ CloudFront │ ─────────► │ S3 (frontend)    │
└────┬────┘               │ E2PEI...   │            │ jimmy-ntcip-...  │
     │                    └────────────┘            └──────────────────┘
     │
     │ Service worker installs, caches: index.html,
     │ manifest.json, icon-192.png, icon-512.png
     ▼
┌──────────────────┐
│ Browser cache    │
│ "ntcip-sim-v2"   │   Subsequent loads: SW intercepts,
└──────────────────┘   serves from cache. Network-only on
                       cache miss. Works fully offline.
```

---

## 4. Current state

### Works end-to-end

- Browser-based NEMA dual-ring 8-phase simulation runs entirely client-side. Animated canvas intersection, live NTCIP 1202 OID values, four control tabs (Timing Plan / Ring-Barrier / NTCIP Objects / Learn NTCIP). Verified live 2026-05-08.
- PWA-installable. After first load, the page works fully offline. Service worker cache key `ntcip-sim-v2`.
- CI auto-deploys on every push to `main`. Two-step workflow: S3 sync + CloudFront invalidation.
- Five timing presets: AM Peak, PM Peak, Off-Peak, Heavy Freight, Ped Priority. Concurrent phase pairs Φ1+Φ5 → Φ2+Φ6 ⟂ Φ3+Φ7 → Φ4+Φ8 with barrier enforcement.
- Mobile-responsive: single-column layout below 900 px viewport; tab bar scrolls horizontally on small screens.

### Open items

- GitHub Actions still pinned to v4 majors (`actions/checkout@v4`, `aws-actions/configure-aws-credentials@v4`), not v6. Other portfolio projects bumped to v6 in May 2026; this repo missed the bump. Tracked as Future Enhancement E1.
- No CloudWatch alarms exist for this project. Tracked as E2.
- `portfolio-user` CLI principal lacks `cloudwatch:GetMetricStatistics` and `ce:GetCostAndUsage` permissions. Tracked as E3.
- Frontend bucket has no lifecycle configuration. Noncurrent versions accumulate; low impact at this traffic level. Not promoted to its own enhancement entry.

---

## 5. Build history

### Phase 1 — Initial scaffold + PWA setup (2026-04-14 → 2026-04-22)

Migrated from a monorepo into a standalone repository (commit `8116e00`). First end-to-end working version with the full simulation engine, canvas rendering, and NTCIP 1202 OID viewer in a single `index.html`. PWA layer added in the same phase: service worker (`sw.js`, cache-first), Web App Manifest (`manifest.json`, `display: standalone`), and a full icon set (192 + 512 + favicons). Service worker cache key bumped `v1` → `v2` during the icon reorganization (`e227814`) to invalidate stale entries. Dead `icons/` directory removed after icons moved to root (`e0d38bd`). README + LICENSE + initial live demo link committed (`a70d172`). At end of phase: working PWA, no backend, manually deployed.

### Phase 2 — CI/CD + subdomain wiring (2026-05-01 → 2026-05-08)

Deploy workflow added (`6539654`). 32-line two-step pipeline: S3 sync (with excludes for `.git`, `.github`, `*.md`, `LICENSE`, `.gitignore`, and the `generate_icons.py` helper) followed by CloudFront invalidation. No Lambda step, no diff-guard, no smoke test — appropriate for a static site with no backend. Subdomain switched from the raw CloudFront URL to `ntcip.jimmyhubbard2.cc` via cPanel CNAME → CloudFront (`778bc5d`). The subdomain matches the protocol name rather than the full project name — shorter and more memorable.

### Portfolio-wide infrastructure note — OAC migration (2026-05-07)

Frontend bucket `jimmy-ntcip-simulator` migrated to Origin Access Control as part of the portfolio-wide OAC standardization across all eight project distributions. No source-code commit in this repo (OAC is a CloudFront + bucket policy change, not a build-artifact change). See Key Decision 4 for the rationale.

---

## 6. Operational reference

### S3 bucket

| Bucket | Purpose | PAB | Encryption | Lifecycle | Project tag |
|---|---|---|---|---|---|
| jimmy-ntcip-simulator | Static frontend | all 4 ON | AES256 | (none) | ntcip-simulator |

### CloudFront

| Field | Value |
|---|---|
| Distribution ID | `E2PEIMT1J3W4MO` |
| Status | Deployed |
| Aliases | `ntcip.jimmyhubbard2.cc` |
| CloudFront domain | `d1r8pxnmau5sot.cloudfront.net` |
| Origin | S3 REST endpoint → `jimmy-ntcip-simulator.s3.us-east-1.amazonaws.com` (OAC-fronted) |
| OAC ID | `E1O8A8ZIM8H8S` |
| Viewer cert source | ACM |
| ACM cert ARN | `arn:aws:acm:us-east-1:603509861186:certificate/598151c8-e0e7-4b46-acf0-4da54e5bce38` |
| Min protocol version | TLSv1.2_2021 |
| Price class | PriceClass_100 (NA + EU) |
| Custom error 403 → | `/index.html` (200) |
| Custom error 404 → | `/index.html` (200) |
| Default root object | `index.html` |
| WAF / WebACL | none |
| Cache behaviors | (DefaultCacheBehavior only) |

### CloudWatch alarms

None currently scoped to this project. Tracked as Future Enhancement E2.

### Cost & utilization

`portfolio-user` CLI principal does not have `cloudwatch:GetMetricStatistics` or `ce:GetCostAndUsage` permissions. 30-day request counts and per-project cost are not queryable from the CLI right now. The `Project=ntcip-simulator` tag is present on every resource for Cost Explorer attribution, but reading the data requires either Console access or an IAM permission grant. Tracked as E3.

---

## 7. Key decisions

### 1. Vanilla HTML/CSS/JS in a single file, no framework, no build step

The complete application is one 48 KB `index.html` with inlined `<style>` and `<script>`. React, Vue, Svelte, or even a multi-file split with ES modules were all viable alternatives. A single-file vanilla approach is easy to read top-to-bottom in any editor, has zero supply-chain attack surface (no `npm install` step in CI), and deploys in seconds via S3 sync. The CI workflow is correspondingly 32 lines — no bundler, no toolchain, no `npm run build`. Cost: harder to maintain if the file grows past ~100 KB (today's 48 KB is comfortable). For a portfolio demo that needs to load fast and be easy for recruiters to inspect, single-file vanilla is the right call.

### 2. PWA implementation for offline demo resilience

The PWA layer exists for one practical reason: I demo this project on a laptop at venues with unreliable WiFi, and the service worker plus offline cache means the simulator runs regardless of network conditions at the demo location. After first load, `index.html`, `manifest.json`, and the icon set are served from the browser cache; the page works fully offline. The implementation is a 30-line cache-first service worker (`sw.js`) plus a `manifest.json` declaring `display: standalone`. No additional infrastructure cost — both files ship as part of the same S3 sync as the rest of the static site.

### 3. Canvas API for intersection rendering (not SVG or DOM)

The intersection visualization is a 440×440 `<canvas>` that redraws every simulation tick (`setInterval` based on `simSpeed`, typically 60-200 ms). SVG and DOM-based approaches would both have worked, but Canvas is the standard choice for tick-based animation at this rate because the rendering pipeline doesn't have to walk a per-element DOM tree on each frame. The trade-off (no accessibility tree, no per-element CSS) is acceptable for an engineering simulation where the audience reads the surrounding controls, not the rendered intersection. The same state object that drives the canvas also drives the phase status bar, ring/barrier diagram, and OID tree — all DOM-rendered. Canvas was the right tool for one specific job inside an otherwise DOM-rendered UI.

### 4. OAC over OAI for the static-site bucket

The frontend bucket is fronted by Origin Access Control rather than the older Origin Access Identity pattern. Bucket policy scoped to `cloudfront.amazonaws.com` service principal with a `SourceArn` condition pinned to distribution `E2PEIMT1J3W4MO`; CloudFront can read, nothing else can. All four Public Access Block settings on. Static website hosting disabled (the bucket uses the S3 REST endpoint via OAC). SPA-style routing handled at CloudFront with `CustomErrorResponses` mapping 403 and 404 to `/index.html` with a 200 response. OAC is the AWS-recommended pattern since 2022: SigV4 signing, support for SSE-KMS bucket encryption (not used here but available), and a more auditable trust model than OAI's anonymous-reader-by-CF-only convention. Migrated 2026-05-07 as part of the portfolio-wide OAC standardization across all eight project distributions.

---

## 8. Future enhancements

### E1 — Bump GitHub Actions to v6 majors (priority: medium)

`.github/workflows/deploy.yml` still pins `actions/checkout@v4` and `aws-actions/configure-aws-credentials@v4`. These v4 actions run on Node.js 20, which is deprecated on the GitHub Actions runner. Two upcoming deadlines from GitHub's deprecation timeline:

- **2026-06-02** — Actions are forced to run on Node.js 24 by default. v4 actions whose internal JS is not Node-24-compatible may behave differently from this date.
- **2026-09-16** — Node.js 20 is removed from the runner entirely. v4 actions will fail to start from this date.

Resume-matcher bumped to v6 in commit `ebd2cee` (2026-05-12); log-analyzer in `6218f76` (2026-05-12). ntcip-simulator and FieldIQ's prewarm.yml are the remaining v4 holdouts in the portfolio. Recommended bump before 2026-06-02 to stay ahead of the force-default. Fix is a two-line edit per workflow file (`@v4` → `@v6` for both actions).

### E2 — CloudWatch alarm for CloudFront 5xx error rate (priority: medium)

Zero alarms exist for this project. The most meaningful metric for a static site is CloudFront 5xx error rate — an origin failure (S3 unreachable, OAC misconfigured, bucket deleted) would surface here. Suggested baseline: `5xxErrorRate >= 1% in 5 min` on distribution `E2PEIMT1J3W4MO`. Less noise than alarming on raw error counts at low traffic. SNS topic with email subscription. One-time setup.

### E3 — Grant `portfolio-user` CLI observability reads (priority: low)

Same enhancement carried over from resume-matcher and log-analyzer. `cloudwatch:GetMetricStatistics` and `ce:GetCostAndUsage` both return AccessDenied for the `portfolio-user` IAM principal. Today this means scripted observability reads fall back to the AWS Console. Acceptable for now, but blocks any future scripted reporting. Granting either inline or via attached managed policies (`CloudWatchReadOnlyAccess` + a Cost Explorer policy) unblocks observability across all eight portfolio projects at once.

---

## 9. Files & structure

```
ntcip-simulator/                       ← Lives on Windows Desktop
├── .github/
│   └── workflows/
│       └── deploy.yml                 ← CI/CD — S3 sync + CloudFront invalidation (32 lines)
├── LICENSE                            MIT
├── README.md                          Recruiter-facing summary (~75 lines)
├── index.html                         Complete app — HTML + CSS + JS in one file (~48 KB)
├── manifest.json                      PWA manifest (installable, display: standalone, landscape)
├── sw.js                              Service worker — cache-first, key ntcip-sim-v2 (30 lines)
├── generate_icons.py                  One-time PWA icon generator (excluded from deploy sync)
├── apple-touch-icon.png
├── favicon-16.png
├── favicon-32.png
├── favicon.ico
├── icon-192.png
└── icon-512.png
```
