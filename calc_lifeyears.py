"""
annual_life_years.py   —   Build an annual world-population series
and total life-years up to the latest anchor (currently 2025).

Interpolation technique
-----------------------
Between every consecutive anchor pair [y0, P0] and [y1, P1] we assume a
straight-line trajectory.  For each integer calendar year y such that
y0 ≤ y < y1:

       P(y) = P0 + (P1 − P0) * (y − y0) / (y1 − y0)

That gives one *mid-year* population estimate per whole year.  Life-years
for that year are simply P(y) × 1 000 000.  Summing from the earliest
anchor through the final anchor year produces cumulative human
life-years.  No other smoothing, splines, or model fitting is applied.

Usage
-----
    python annual_life_years.py          # reads anchor_pops.csv locally
    python annual_life_years.py https://raw.githubusercontent.com/alexjchen00/lifeyears/main/anchor_pops.csv

Outputs
-------
  • anchor_pop_annual_to_2025.csv   (Year, Population_Millions, Life_Years)
  • prints the grand-total life-years to stdout
"""

import sys, pandas as pd, numpy as np, pathlib

# ----------------------------------------------------------------------
# 1. Load the anchor grid
# ----------------------------------------------------------------------
src = sys.argv[1] if len(sys.argv) == 2 else "anchor_populations.csv"
anchor = (pd.read_csv(src, usecols=["Year", "Population_Millions"])
            .sort_values("Year")
            .reset_index(drop=True))

# ----------------------------------------------------------------------
# 2. Interpolate annually from first anchor to last anchor (inclusive)
# ----------------------------------------------------------------------
START = int(anchor["Year"].min())
END   = int(anchor["Year"].max())          # latest anchor (e.g. 2025)

rows = []
for i in range(len(anchor) - 1):
    y0, p0 = int(anchor.loc[i, "Year"]),   anchor.loc[i, "Population_Millions"]
    y1, p1 = int(anchor.loc[i+1, "Year"]), anchor.loc[i+1, "Population_Millions"]

    for y in range(y0, y1):
        frac = 0 if y == y0 else (y - y0) / (y1 - y0)
        rows.append((y, p0 + frac * (p1 - p0)))

# add the final anchor year itself
rows.append((END, anchor.loc[anchor["Year"] == END,
                             "Population_Millions"].iloc[0]))

annual = pd.DataFrame(rows, columns=["Year", "Population_Millions"])
annual["Life_Years"] = (annual["Population_Millions"] * 1_000_000).astype(int)

# ----------------------------------------------------------------------
# 3. Write out & report the total
# ----------------------------------------------------------------------
out = pathlib.Path("anchor_pop_annual_to_2025.csv")
annual.to_csv(out, index=False)

total = int(annual["Life_Years"].sum())
print(f"Total human life-years (through {END}): {total:,}")
print(f"Annual CSV written to {out.resolve()}")
