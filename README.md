<p align="center">
  <img src="docs/icon.png" width="96" alt="CS2 Climate Calculator icon">
</p>

<h1 align="center">CS2 Climate Calculator</h1>

<p align="center">
Turns real-world city climate data into <b>Cities: Skylines II</b> climate settings —<br>
by simulating the game's own weather generator and solving it backwards.
</p>

---

## Features

- **Load a real city's climate by name** — parses the climate table (`{{Weather box}}`) from the
  city's Wikipedia article, including transcluded weatherbox templates, °F → °C and inch → mm
  conversion, and sunshine-hours → percent-of-possible conversion (latitude-based day length).
- **Open-Meteo ERA5 fallback** — for places without a Wikipedia climate table (or with missing
  rows), 30 years of daily reanalysis data (1991–2020) are aggregated into monthly normals. Works
  by city name or raw coordinates, and can fill individual missing rows.
- **Every CS2 climate field**, not just the computed ones:
  - *Global*: Name, Latitude, Longitude, Max Sun Elevation, Sun Elevation Clamp Start, Freezing
    Temperature, Random Seed, Default Weather Prefab / Default Weathers.
  - *Per season*: Season Prefab, Start Time, Temperature Night/Day + Deviations, Clouds
    Chance/Amount/Deviation, Precipitation Chance/Amount/Deviation, Turbulence, Aurora
    Chance/Strength.
- **Shows what the game will actually do** — every season card puts the simulated in-game result
  next to the real climate, so nothing is taken on faith.
- **Southern-hemisphere aware** — seasons and start times flip automatically (Winter = JJA).
- Editable monthly data table with instant recalculation, per-season copy / copy-all / JSON
  export, monthly climate charts, and automatic session restore.

## How it works — the game's own generator, run in reverse

The values are **solved, not fitted with formulas**. `ClimatePrefab.RebuildCloudinessCurves` and
`RebuildPrecipitationCurves` (decompiled from `Game.dll`) are reimplemented here exactly — Unity's
simplex noise, its truncated gaussian draws, its animation curves and tangent smoothing — so the
app can bake the same year the game will bake. It then searches for the season parameters whose
simulated year reproduces the real climate.

What the decompiled generator does, per sample of the 12-day game year:

```
amount  = gaussian(Amount ± Deviation)               // one draw per game-day
amount += simplexNoise(t*4) * Turbulence * amount
if noise(t) > Chance:  amount *= 1 - (noise - Chance) * 2
precipitation fades below 0.7 / 0.4 cloudiness, and is forced to 0 below 0.2
```

Three consequences drive everything this app does:

- **Rain only stops once `noise >= Chance + 0.5`.** At the game's default Chance of 30 it
  precipitates **54% of the year**; even Chance 0 rains a third of the time unless the clouds are
  thin. This is why vanilla maps feel permanently wet.
- **The game calls it sunny when `cloudiness <= 0.5 and precipitation == 0`**, so drizzle eats
  sunshine. Real sunshine and real rain frequency cannot both be matched — the selector above the
  cards decides which one wins.
- **The Random Seed matters more than the parameters.** A game year is 12 days, so a season holds
  only three random draws: one fixed parameter set swings between 15% and 85% sunshine across
  seeds. The app scans seeds, keeps the one that lands closest to the real climate, and refits the
  parameters for it — so use the seed it gives you.

Temperature needs no search: the game draws each game-day around the season means, so those are
used directly, with Deviation set to the 90th-percentile daily spread the game expects
(`sigma / 0.78`, sigma estimated from the mean monthly extremes via `|extreme - daily| / 2.04`).
Precipitation Amount is solved so the mean precipitation value matches the real rainfall rate,
reading `precipitation 1.0 = 10 mm/h`.

Typical result (Charleston, South Carolina — real → simulated in-game):

| Season | Sunny | Rain time | Water |
|---|---|---|---|
| Winter | 57% → 56% | 10% → 10% | 84 → 84 mm/mo |
| Spring | 69% → 71% | 10% → 13% | 84 → 84 mm/mo |
| Summer | 64% → 65% | 19% → 20% | 166 → 211 mm/mo |
| Autumn | 61% → 58% | 13% → 15% | 110 → 105 mm/mo |

## Superseded: the original formula document

Earlier releases implemented *Formula for Climate Settings* (season means, `days x 6` for
Precipitation Chance, intensity `x 6.25` for Amount) and then a series of corrections to it. All of
that is gone: the decompiled generator showed that a day-count approach cannot describe how the
engine actually gates rain. Temperature is the one part that carried over, now with a deviation
derived from the game's own constant rather than a fitted multiplier.

## Accuracy notes

- **Prefer Wikipedia when available** — those tables are official station normals from national
  weather services.
- **ERA5 caveats** — reanalysis is gridded model output: it over-counts light-drizzle days and
  smooths temperature in complex terrain and urban heat islands. It does supply one thing
  Wikipedia cannot: measured hours of precipitation per month, which is exactly what the
  rain-frequency target needs. Without it the app infers wet hours from the water and a
  ~1.2 mm/h typical rate.
- **Some targets are unreachable** — a very gloomy winter (Moscow at 16% sunshine) is beyond what
  the cloud gate can produce. The card shows what the game will actually do, so the gap is visible
  rather than hidden.
- **Aurora and Sun Elevation Clamp Start** are estimates (no published game formula) — both are
  editable in the UI.

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
