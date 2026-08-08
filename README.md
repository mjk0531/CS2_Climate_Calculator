<p align="center">
  <img src="docs/icon.png" width="96" alt="CS2 Climate Calculator icon">
</p>

<h1 align="center">CS2 Climate Calculator</h1>

<p align="center">
Turns real-world city climate data into climatologically accurate<br>
<b>Cities: Skylines II</b> climate settings — every field the editor's climate section needs.
</p>

---

## Features

- **Load a real city's climate by name** — parses the climate table (`{{Weather box}}`) from the city's Wikipedia article, including transcluded weatherbox templates, °F → °C and inch → mm conversion, and sunshine-hours → percent-of-possible conversion (latitude-based day length).
- **Open-Meteo ERA5 fallback** — for places without a Wikipedia climate table (or with missing rows), 30 years of daily reanalysis data (1991–2020) are aggregated into monthly climate normals. Works by city name or raw coordinates. Missing rows can be filled individually.
- **Every CS2 climate field**, not just the computed ones:
  - *Global*: Name, Latitude, Longitude, Max Sun Elevation (computed from latitude), Sun Elevation Clamp Start, Freezing Temperature, Random Seed, Default Weather Prefab / Default Weathers.
  - *Per season*: Season Prefab, Start Time (fraction of year), Temperature Night/Day + Deviations, Clouds Chance/Amount/Deviation, Precipitation Chance/Amount/Deviation, Turbulence, Aurora Chance/Strength (latitude-based estimate).
- **Southern-hemisphere aware** — seasons and start times flip automatically (Winter = JJA, starting Jun 1).
- Editable monthly data table with instant recalculation, per-season copy / copy-all / JSON export, monthly climate charts, and automatic session restore.

## The formulas

Implemented from the document *Formula for Climate Settings*, validated against the official CS2 **San Francisco** prefab (values match within ±10%).

| CS2 field | Formula (per season, monthly values averaged) |
|---|---|
| Temperature Night / Day | mean of monthly daily min / max |
| Temperature Deviation | `max(2.5, σ(monthly) × 1.5)`; if mean-extreme rows exist, also `\|daily − extreme\| / 1.5`, take the larger |
| Clouds Amount | `100 − sunshine %` |
| Clouds Chance | `min(100, Clouds Amount × 1.5)` |
| Clouds Amount Deviation | `clamp(15 + σ(monthly cloud %), 15, 30)` |
| Precipitation Chance | **v3 (default):** realistic wet-time — `mm ÷ (rate × hours in month) × 3`, rate from warmth & convectivity · **v2:** `days × factor × (1 − 0.5 × convectivity)` · **v1:** `days × 6` |
| Precipitation Amount | **v2:** intensity soft-knee (mm/day above 11 counts half) `× 6.25` · **v1:** raw `× 6.25` |
| Precip. Amount Deviation | `clamp(Amount × 0.25, 10, 30)` |
| Turbulence | `min(0.8, max(0.1, intensity/25 × temp_factor × (1 + 0.5 × convectivity)))` |

### The v4 precipitation chance (default — from decompiled game code)

Decompiling `Game.Prefabs.Climate.ClimatePrefab.RebuildPrecipitationCurves` shows how CS2
actually consumes these values: precipitation is baked as `gaussian(Amount ± Deviation)`,
attenuated by `×(1 − (noise − Chance)×2)` where the noise field is centered at 0.5, and hard-
zeroed only when baked cloudiness < 0.2. **Rain fully stops only when noise ≥ Chance + 0.5** —
that offset means Chance ≥ 50 produces near-nonstop rain (why vanilla over-rains), and even
Chance = 0 leaves attenuated rain about half the cloudy time. v4 inverts this gate so the share
of time with *visible* rain matches the physical wet-time; for most real climates that solves to
**0–10**, which is the correct range for this engine. The engine cannot rain less than its
floor (~15–30% of cloudy time at Chance 0) without also lowering the cloud values.

### The v3 precipitation chance (selectable)

CS2 consumes Precipitation Chance roughly as a *share of time* — and the official prefabs
already over-rain (a widespread vanilla complaint). So v3 ignores prefab anchoring and computes
the physically real share of hours precipitation falls: `monthly mm ÷ (precip rate × hours in
month)`, where the rate runs from light snow (0.6 mm/h) through warm stratiform rain (2.0 mm/h)
to convective downpours (~9 mm/h), times a ×3 gameplay-presence boost. Wet-day counts cancel out
of the math entirely, so counting-threshold differences stop mattering. Typical results: Seoul
monsoon 60, Moscow winter snow 33, San Francisco winter 27, Charleston summer thunderstorms 9
(with Amount 75 and Turbulence 0.74 — rare, violent, fast-changing). The **Chance ×** control
scales any model to taste; ~33% gives strict physical realism.

### The v2 precipitation model (selectable, prefab-anchored)

"Precipitation days" counts a day even if it only rained for one afternoon hour — which makes
day-count-based Chance badly overstate warm convective climates (Charleston, Miami: brief
thunderstorms) while being right for long frontal/monsoon rain. v2 fixes this with two ideas:

- **Threshold-aware factor** — the doc's ×6 was the midpoint of the factors implied by the
  official prefabs (SF 6.5, days counted at ≥0.01 in; Tampere 5.5, at ≥0.1 mm). v2 reads the
  climate table's declared counting threshold (`unit precipitation days`) and uses 5.5 (<0.2 mm)
  or 6.5 (≥0.2 mm) — restoring both prefab anchors exactly.
- **Convectivity** = `warm((T−15)/10) × sunny((sun% − 40)/30)`, each clamped 0–1. Hot seasons that
  stay sunny despite rain = short afternoon storms → Chance discounted up to −50% and Turbulence
  boosted up to +50% (storm cells cycle weather faster). Overcast monsoon (Seoul jangma, Mumbai)
  and frontal rain (London, Seattle) score ~0 and are untouched.

Validated across **64 cities** covering every major regime — mediterranean, oceanic drizzle,
subtropical thunderstorm belts (US Gulf/Southeast, Brisbane, Buenos Aires), East/South Asian
monsoon, equatorial, desert, continental snow, subarctic, highland: convective climates drop
(Miami summer 100→59, Houston 55→33, Chicago 60→41), everything else stays within a few points.

> **Note on Tampere:** the official Tampere prefab is hand-tuned for aurora gameplay and snow visuals, so real-climate values intentionally differ. This app computes the real-climate-accurate values.

## Accuracy notes

- **Prefer Wikipedia when available** — those tables are official station normals from national weather services, and the formulas were calibrated against that kind of data.
- **ERA5 caveats** — reanalysis is gridded model output: it over-counts light-drizzle days (raise the wet-day threshold to ≥ 1.0 mm to compensate) and smooths temperature in complex terrain and urban heat islands.
- **Aurora and Sun Elevation Clamp Start** are reasonable estimates (no published game formula) — both are editable in the UI.

## Run it

- **Windows**: download `CS2-Climate-Calculator.exe` from [Releases](../../releases) — portable, no install. SmartScreen may warn on first run (unsigned binary): *More info → Run anyway*.
- **Any browser**: just open `index.html`. Wikipedia and Open-Meteo both allow cross-origin requests, so no server is needed.

## Build from source

```bash
npm install
npx electron-builder --win portable
```

The exe appears in `dist/`. Tip: build from a plain local folder — npm inside cloud-synced directories (OneDrive etc.) can be flaky.

The app icon is generated by `scripts/make_icon.py` (Python + Pillow):

```bash
python scripts/make_icon.py
```

## License

[MIT](LICENSE)
