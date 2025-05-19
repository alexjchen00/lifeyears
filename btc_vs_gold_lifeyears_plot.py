# ----------  Bitcoin vs Gold life-years ratio (2009-2100)  ----------
import pandas as pd, numpy as np, matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

# --- load canonical data ---
anchor = pd.read_csv("anchor_pops.csv").sort_values("Year")          # anchors → 2025
proj   = pd.read_csv("UNWPP2022_Medium_Variant_World_Pop_2025_2100.csv").sort_values("Year")  # 5-yr points 2025-2100

# --- build annual world-population series to 2100 ---
rows = []
# (a) anchors → 2025
for i in range(len(anchor) - 1):
    y0, p0 = anchor.iloc[i][["Year", "Population_Millions"]]
    y1, p1 = anchor.iloc[i + 1][["Year", "Population_Millions"]]
    for y in range(int(y0), int(y1)):
        rows.append((y, p0 + (p1 - p0) * (y - y0) / (y1 - y0)))
rows.append((2025, anchor.loc[anchor["Year"] == 2025, "Population_Millions"].iloc[0]))

# (b) UN projections 2025 → 2100
for i in range(len(proj) - 1):
    y0, p0 = proj.iloc[i][["Year", "Population_Millions"]]
    y1, p1 = proj.iloc[i + 1][["Year", "Population_Millions"]]
    for y in range(int(y0) + 1, int(y1) + 1):            # include y1
        rows.append((y, p0 + (p1 - p0) * (y - y0) / (y1 - y0)))

annual = pd.DataFrame(rows, columns=["Year", "Pop_M"]).sort_values("Year")
annual["Life_Y"] = annual["Pop_M"] * 1_000_000

# --- cumulative life-years ---
gold_start = -700     # gold store-of-value clock
btc_start  =  2009
annual["GoldCum"] = np.where(annual["Year"] >= gold_start, annual["Life_Y"], 0).cumsum()
annual["BTCCum"]  = np.where(annual["Year"] >= btc_start,  annual["Life_Y"], 0).cumsum()
annual["Ratio"]   = annual["BTCCum"] / annual["GoldCum"]

# --- plot from 2009 onward ---
plot = annual[annual["Year"] >= 2009]

plt.figure(figsize=(10, 6))
plt.plot(plot["Year"], 100 * plot["Ratio"], color="orange", linewidth=2.5)

# y-axis 0 – 50 %
plt.ylim(0, 50)
plt.yticks(np.arange(0, 51, 10))
plt.gca().yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"{y:.0f}%"))

plt.title("Bitcoin vs Gold Lindyness\nMeasured by Life-Years (gold clock starts 700 BCE)\nUN WPP 2022 medium-variant projection from 2026 onward")
plt.xlabel("Year")
plt.ylabel("Bitcoin / Gold Life-Years (%)")
plt.grid(True, linestyle="--", alpha=0.3)

# annotate ‘now’ (2025)
now_y = plot.loc[plot["Year"] == 2025, "Ratio"].values[0] * 100
plt.scatter(2025, now_y, color="red")
plt.annotate(f"2025: {now_y:.2f}%", (2025, now_y),
             xytext=(0, 10), textcoords="offset points",
             ha="center", color="red")

plt.tight_layout()
plt.show()
