"""Build data/postcodes.js for the "How much better will it be for me?" box.

For each of the 151 public towns (farm-rain-forecast's regional_points.csv; customer farms are left out): how much more
accurate the emailed chance of 1 mm+ was than a typical single weather model (the mean Brier score of the 7 ensemble
models), days 1-3 and 4-7, reports 2 Jan - 5 Nov 2026, against SILO. Same rows and method as
farm-rain-forecast/research/full_blend_retests/vs_average/chances_vs_average.py.
Then each postcode (GeoNames AU, CC BY 4.0; the mean location of its places) gets its nearest town and the distance.

    cd farm-rain-forecast && FARM_RAIN_FORECAST=. uv run --quiet --with pyarrow python -I ../raindrop-website/tools/build_postcodes.py
"""
import json
import os
import sys
from pathlib import Path

REPO = Path(os.environ.get("FARM_RAIN_FORECAST", "../farm-rain-forecast")).resolve()  # the private forecast repo
SITE = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(REPO / "research/full_blend_retests/wn3_share"), str(REPO)]
import guard  # noqa: F401,E402  (kills this process above 4 GB)
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from rain_forecast import calibrated_chance_1mm  # noqa: E402

MEMBER = ["ifs", "aifs", "gefs", "gem", "icon", "ukmo", "wn2m"]
COVERED = {"VIC", "NSW", "QLD", "SA", "ACT"}

towns = pd.read_csv(REPO / "regional_points.csv")
m = pd.read_parquet(REPO / "data/research/ml/full_blend_means_east.parquet", columns=["point", "R", "k", "silo", "wn3", *MEMBER])
c = pd.read_parquet(REPO / "data/research/ml/full_blend_chances_east.parquet",
                    columns=["point", "R", "k", *[f"p{t}_{s}" for t in (1, 5) for s in MEMBER]])
for x in (m, c):
    x["point"] = x.point.astype(str)
d = m.merge(c, on=["point", "R", "k"], how="left")
d = d[d.point.isin(towns.id) & d.R.between("2026-01-02", "2026-11-05") & d.k.between(1, 7) & d.silo.notna()
      & d.wn3.notna() & d[["ifs", "aifs", "gefs", "wn2m"]].notna().all(axis=1)].reset_index(drop=True)
d["shown"] = calibrated_chance_1mm(d[[f"p1_{s}" for s in MEMBER]].mean(axis=1), d[[f"p5_{s}" for s in MEMBER]].mean(axis=1), d.k)
y = (d.silo >= 1).astype(float)
single = pd.DataFrame({s: (d[f"p1_{s}"] - y) ** 2 for s in MEMBER}).mean(axis=1)  # per row, the models present
d["se_email"], d["se_single"] = (d.shown - y) ** 2, single
d["band"] = np.where(d.k <= 3, "d13", "d47")
g = d.groupby(["point", "band"])[["se_email", "se_single"]].mean()
gain = (100 * (1 - g.se_email / g.se_single)).unstack()
rows = d.groupby("point").size()
print(f"towns scored: {len(gain)} of {len(towns)}; rows per town {rows.min()}-{rows.max()}")
print(gain.describe().round(1).to_string())
print("towns where the email is worse than the typical model:", gain[(gain < 0).any(axis=1)].round(1).to_dict("index"))

towns = towns.set_index("id").loc[gain.index].reset_index()
town_list = [[t.name, t.state, round(float(gain.at[t.id, "d13"])), round(float(gain.at[t.id, "d47"]))] for t in towns.itertuples()]

geo = pd.read_csv(SITE / "tools/geonames/AU.txt", sep="\t", header=None, dtype={1: str},
                  usecols=[1, 4, 9, 10], names=["postcode", "state", "lat", "lon"])
pc = geo.groupby("postcode").agg(state=("state", "first"), lat=("lat", "mean"), lon=("lon", "mean"))
lat1, lon1 = np.radians(pc.lat.to_numpy())[:, None], np.radians(pc.lon.to_numpy())[:, None]
lat2, lon2 = np.radians(towns.lat.to_numpy())[None, :], np.radians(towns.lon.to_numpy())[None, :]
km = 6371 * 2 * np.arcsin(np.sqrt(np.sin((lat2 - lat1) / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2))
nearest, dist = km.argmin(axis=1), km.min(axis=1)
postcodes = {p: ([int(i), int(round(k))] if s in COVERED else [-1, 0]) for p, s, i, k in zip(pc.index, pc.state, nearest, dist)}
covered = pc.state.isin(COVERED)
print(f"postcodes: {len(pc)}, covered {int(covered.sum())}; nearest town km: median {np.median(dist[covered]):.0f}, "
      f"90th pct {np.percentile(dist[covered], 90):.0f}, max {dist[covered].max():.0f}")

data = {"period": "Jan to Nov 2026", "towns": town_list, "postcodes": postcodes}
out = SITE / "data/postcodes.js"
out.write_text("// Built by tools/build_postcodes.py; postcode locations from GeoNames (CC BY 4.0)\n"
               f"window.RAIN_DROP_DATA = {json.dumps(data, separators=(',', ':'), ensure_ascii=False)};\n")
print(f"wrote {out} ({out.stat().st_size / 1e3:.0f} kB)")
