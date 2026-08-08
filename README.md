<p align="center">
  <img src="docs/icon.png" width="96" alt="CS2 Climate Calculator icon">
</p>

<h1 align="center">CS2 Climate Calculator</h1>

<p align="center">
Turns real-world city climate data into climatologically correct<br>
<b>Cities: Skylines II</b> climate settings — every field the editor's climate section needs.
</p>

---

## Features

- **Load a real city's climate by name** — parses the climate table (`{{Weather box}}`) from the
  city's Wikipedia article, including transcluded weatherbox templates, °F → °C and inch → mm
  conversion, and sunshine-hours → percent-of-possible conversion (latitude-based day length).
- **Open-Meteo ERA5 fallback** — for places without a Wikipedia climate table (or with missing
  rows), 30 years of daily reanalysis data (1991–2020) are aggregated into monthly climate
  normals. Works by city name or raw coordinates, and can fill individual missing rows.
- **Every CS2 climate field**, not just the computed ones:
  - *Global*: Name, Latitude, Longitude, Max Sun Elevation (from latitude), Sun Elevation Clamp
    Start, Freezing Temperature, Random Seed, Default Weather Prefab / Default Weathers.
  - *Per season*: Season Prefab, Start Time, Temperature Night/Day + Deviations, Clouds
    Chance/Amount/Deviation, Precipitation Chance/Amount/Deviation, Turbulence, Aurora
    Chance/Strength.
- **Southern-hemisphere aware** — seasons and start times flip automatically (Winter = JJA).
- Editable monthly data table with instant recalculation, per-season copy / copy-all / JSON
  export, monthly climate charts, and automatic session restore.

## The formulas

Implemented from the document *Formula for Climate Settings*, validated there against the official
CS2 **San Francisco** prefab (within ±10%).

Inputs, per month, averaged over each season: `x` = precipitation (mm), `y` = precipitation days,
`z` = percent possible sunshine.

| CS2 field | Formula |
|---|---|
| Temperature Night / Day | mean daily minimum / maximum |
| Temperature Deviation | `max(2.5, σ(monthly) × 1.5)`; where mean-extreme rows exist, also `\|daily − extreme\| / 1.5`, take the larger |
| Clouds Amount | `100 − z` |
| Clouds Chance | `min(100, Clouds Amount × 1.5)` |
| Clouds Amount Deviation | `clamp(15 + σ(monthly cloud %), 15, 30)` |
| Precipitation Chance | `y × h / hours in month`, where `h = clamp(4 + (x/y)/2, 4, 16)` hours of rain per rainy day — see below |
| Precipitation Amount | `min(100, avg(x / y) × 6.25)` — daily rain intensity on a 0–100 scale |
| Precip. Amount Deviation | `clamp(Amount × 0.25, 10, 30)` |
| Turbulence | `min(0.8, max(0.1, intensity / 25 × temp_factor))`, `temp_factor = clamp((daily mean + 5) / 15, 0.2, 1.0)` |

### One deviation from the document: Precipitation Chance

The document uses `rainy_days × 6`, which treats every precipitation day as a whole wet day — and
in game that reads far too rainy. A precipitation day is not a day of rain: it carries roughly
four hours of rain plus half an hour for every extra millimetre it drops (capped at 16), so
Precipitation Chance is the resulting **share of time it is actually raining**.

Checked against 30 years of measured precipitation hours (ERA5, 1991–2020):

| | Winter | Spring | Summer | Autumn |
|---|---|---|---|---|
| San Francisco | 14 *(16)* | 7 *(9)* | 1 *(1)* | 4 *(5)* |
| Charleston | 11 *(11)* | 10 *(10)* | 18 *(22)* | 12 *(14)* |
| Seoul | 4 *(6)* | 8 *(10)* | 22 *(24)* | 9 *(10)* |
| Moscow | 20 *(17)* | 14 *(14)* | 14 *(16)* | 17 *(16)* |
| London | 10 *(14)* | 7 *(15)* | 8 *(15)* | 10 *(14)* |

*(computed, measured in italics)*. London is the known outlier: it drizzles far more often than it
rains, and ERA5 counts any hour above 0.1 mm. The **Rain time ×%** control scales the whole
column if it still feels off in game.

Fields the document does not cover are derived so the whole climate section can be filled in:
Start Time from the season boundaries, Max Sun Elevation as `clamp(90 − |lat| + 23.44, 45, 90)`
with the clamp start 15° below it, and Aurora from latitude (zero below ~50°, scaling to ~68°,
suppressed during bright high-latitude summers).

> **Note on Tampere:** the official Tampere prefab is hand-tuned for aurora gameplay and snow
> visuals, so real-climate values intentionally differ. This app computes the real-climate-accurate
> values.

## Accuracy notes

- **Prefer Wikipedia when available** — those tables are official station normals from national
  weather services, and the formulas were calibrated against that kind of data.
- **ERA5 caveats** — reanalysis is gridded model output: it over-counts light-drizzle days (raise
  the wet-day threshold to ≥ 1.0 mm to compensate) and smooths temperature in complex terrain and
  urban heat islands.
- **Aurora and Sun Elevation Clamp Start** are estimates (no published game formula) — both are
  editable in the UI, as is every value on the cards.

## Run it

- **Windows**: download `CS2-Climate-Calculator.exe` from [Releases](../../releases) — portable, no
  install. SmartScreen may warn on first run (unsigned binary): *More info → Run anyway*.
- **Any browser**: just open `index.html`. Wikipedia and Open-Meteo both allow cross-origin
  requests, so no server is needed.

## Build from source

```bash
npm install
npx electron-builder --win portable
```

The exe appears in `dist/`. Tip: build from a plain local folder — npm inside cloud-synced
directories (OneDrive etc.) can be flaky.

The app icon is generated by `scripts/make_icon.py` (Python + Pillow):

```bash
python scripts/make_icon.py
```

## License

[MIT](LICENSE)
