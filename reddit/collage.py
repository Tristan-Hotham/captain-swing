"""r/dataisbeautiful collage: Captain Swing, did the riots follow the machines? (2400 x 3000 px, light straw background).
Reads ../data/results.json, ../data/parishes.csv, ../data/machines.csv, ../work/parish_shapes.json, ../work/outline.json.
Fonts: FONT_DIR with FrauncesVar.ttf, Source Serif 4, IBM Plex Mono.
Run: python3 collage.py
"""
import os, json
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.collections import PolyCollection
from pyproj import Transformer

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, ".."); D = os.path.join(ROOT, "data"); W = os.path.join(ROOT, "work")
F = os.environ.get("FONT_DIR", "/tmp/claude-0/-home-claude/c232619d-81e0-53f3-9de6-41e973630753/scratchpad/fonts") + "/"
for f in ["FrauncesVar.ttf", "IBMPlexMono-Regular.ttf", "IBMPlexMono-Medium.ttf", "SourceSerif4-Regular.ttf", "SourceSerif4-Semibold.ttf", "SourceSerif4-It.ttf"]:
    fm.fontManager.addfont(F + f)
DISP = fm.FontProperties(fname=F + "FrauncesVar.ttf", weight=900)
SER = "Source Serif 4"; MONO = "IBM Plex Mono"
BG = "#F4EDDC"; FG = "#211F1A"; MUT = "#6E6657"; LAND = "#E6DCC3"; EDGE = "#CFC09F"
FIRE = "#C2410C"; STEEL = "#2F5269"; STRAW = "#A87E22"; ASH = "#9C9383"

R = json.load(open(os.path.join(D, "results.json")))
par = pd.read_csv(os.path.join(D, "parishes.csv")); mach = pd.read_csv(os.path.join(D, "machines.csv"))
shapes = json.load(open(os.path.join(W, "parish_shapes.json"))); OL = json.load(open(os.path.join(W, "outline.json")))["rings"]
TR = Transformer.from_crs(4326, 27700, always_xy=True)
mach["x"], mach["y"] = TR.transform(mach.in_lon.values, mach.in_lat.values)
from matplotlib.colors import to_rgb
def mix(a, b, t): a, b = np.array(to_rgb(a)), np.array(to_rgb(b)); return tuple(a + (b - a) * t)
RAMP = [mix(LAND, FIRE, t) for t in (.35, .58, .8, 1.0)]

fig = plt.figure(figsize=(12, 15), dpi=200, facecolor=BG)
# ---- title
fig.text(.045, .972, "CAPTAIN SWING · ENGLAND AND WALES · 1830 TO 1832", family=MONO, fontsize=13, color=FIRE, va="top", weight="medium")
r = fig.canvas.get_renderer(); x = .045
for word, c in [("Did", FG), ("the", FG), ("riots", FIRE), ("follow", FG)]:
    t = fig.text(x, .955, word, fontproperties=DISP, fontsize=56, color=c, va="top"); x += t.get_window_extent(renderer=r).width / fig.bbox.width + .016
x = .045
for word, c in [("the", FG), ("machines?", STEEL)]:
    t = fig.text(x, .905, word, fontproperties=DISP, fontsize=56, color=c, va="top"); x += t.get_window_extent(renderer=r).width / fig.bbox.width + .016
fig.text(.045, .848, f"In 1830 farm labourers smashed threshing machines and burned ricks across southern and eastern England.\n"
         f"I mapped {R['counts']['incidents_all']:,} Swing incidents and {R['counts']['machines_all']:,} recorded machines in {R['counts']['parishes_all']:,} parishes, using Caprettini\n"
         "and Voth's open data, to ask whether the riots followed the machines, or poverty, enclosure and London.",
         family=SER, fontsize=14.5, color=FG, va="top", linespacing=1.42)

# ---- hero map: parish choropleth with machine squares
ax = fig.add_axes([.0, .315, .60, .465])
for rg in OL:
    a = np.array(rg); ax.fill(a[:, 0], a[:, 1], facecolor=LAND, edgecolor=EDGE, lw=.6, zorder=0)
verts, cols = [], []
for i, rs in enumerate(shapes):
    v = par.SWING.iloc[i]
    if not rs or v <= 0: continue
    k = 0 if v == 1 else 1 if v <= 3 else 2 if v <= 6 else 3
    for d in rs:
        q = np.cumsum(np.array(d).reshape(-1, 2), axis=0) / 1000.0
        xx, yy = TR.transform(q[:, 0], q[:, 1]); verts.append(np.c_[xx, yy]); cols.append(RAMP[k])
ax.add_collection(PolyCollection(verts, facecolors=cols, edgecolors="none", zorder=1))
ax.scatter(mach.x, mach.y, s=7, marker="s", color=STEEL, lw=0, zorder=3, alpha=.9)
ax.set_aspect("equal"); ax.axis("off"); ax.set_xlim(150000, 660000); ax.set_ylim(-60000, 660000)
lx, ly = 155000, 655000
ax.text(lx, ly, "SWING INCIDENTS\nPER PARISH", family=MONO, fontsize=10, color=MUT, va="top", linespacing=1.3)
for j, (lab, c) in enumerate(zip(["1", "2 to 3", "4 to 6", "7 or more"], RAMP)):
    yy = ly - 62000 - j * 22000
    ax.add_patch(plt.Rectangle((lx, yy - 7000), 14000, 14000, color=c)); ax.text(lx + 22000, yy, lab, family=MONO, fontsize=10, color=FG, va="center")
yy = ly - 62000 - 4 * 22000 - 22000
ax.scatter([lx + 7000], [yy], s=14, marker="s", color=STEEL); ax.text(lx + 22000, yy, "recorded\nmachine", family=MONO, fontsize=10, color=FG, va="center", linespacing=1.2)
yy -= 52000
ax.add_patch(plt.Circle((lx + 7000, yy), 7000, fill=False, ls=(0, (2, 2)), lw=1, color=STRAW)); ax.text(lx + 22000, yy, "100 km\nfrom London", family=MONO, fontsize=10, color=STRAW, va="center", linespacing=1.2)
kx, ky = TR.transform(1.113426, 51.15782)
ax.annotate(f"Kent: first machines broken,\nbut only {R['counties']['top'][0]['machines']} machines on record", xy=(kx - 8000, ky + 8000), xytext=(kx - 150000, ky - 175000), family=MONO, fontsize=10.5, color=FG,
            arrowprops=dict(arrowstyle="-", color=FG, lw=.8), zorder=9, ha="left")
lnx, lny = TR.transform(-0.1275, 51.50722)
ax.add_patch(plt.Circle((lnx, lny), 100000, fill=False, ls=(0, (4, 3)), lw=1.2, color=STRAW, zorder=5))
ax.text(lnx - 75000, lny - 112000, f"{R['london']['within100_share'] * 100:.0f}% of parishes inside the ring rioted", family=MONO, fontsize=10, color=STRAW, ha="center", va="top")

# ---- headline numbers
M = R["machines"]; G = R["gradients"]
tx = fig.add_axes([.61, .32, .36, .44]); tx.axis("off")
items = [(f"{M['riot_share_with'] * 100:.0f}% vs {M['riot_share_without'] * 100:.0f}%", STEEL, "of parishes rioted, with and\nwithout a recorded machine:\nabout twice the rate"),
         (f"+{R['neighbours']['diff'] * 100:.0f} points", STEEL, f"machine parishes against their\nmachine-free neighbours ({R['neighbours']['radius_km']} km)"),
         (f"{M['riot_parishes_without_machine_share'] * 100:.0f}%", FIRE, "of riotous parishes had\nno machine on record at all"),
         (f"{G['poor']['rows'][0]['riot_share'] * 100:.0f}% to {G['poor']['rows'][-1]['riot_share'] * 100:.0f}%", FIRE, f"rioted, lowest to highest fifth of\npoor relief per head ({G['poor']['n']:,} parishes)")]
for i, (big, c, small) in enumerate(items):
    y = 1 - i * .25
    tx.text(0, y, big, fontproperties=DISP, fontsize=38, color=c, va="top", transform=tx.transAxes)
    tx.text(0, y - .085, small, family=SER, fontsize=14, color=FG, va="top", transform=tx.transAxes, linespacing=1.3)

# ---- bottom row: three small charts
fig.text(.045, .298, "THE RIVAL SUSPECTS   ·   share of parishes with Swing unrest, lowest to highest fifth of each measure", family=MONO, fontsize=11, color=MUT)
s1 = fig.add_axes([.27, .125, .40, .145]); s1.set_facecolor(BG)
rows = [("Recorded machine (none, any)", [M["riot_share_without"], M["riot_share_with"]], STEEL),
        ("Poor rates per head, 1801", [r["riot_share"] for r in G["poor"]["rows"]], FIRE),
        ("Winter unemployment, 1834", [r["riot_share"] for r in G["unemp"]["rows"]], FIRE),
        ("Enclosure of commons by 1820", [r["riot_share"] for r in G["enclosures"]["rows"]], STRAW),
        ("Wheat price, 1820s", [r["riot_share"] for r in G["wheat"]["rows"]], ASH)]
for i, (lab, pts, c) in enumerate(rows):
    yy = len(rows) - 1 - i
    s1.plot(pts, [yy] * len(pts), color=c, lw=1.6, alpha=.55)
    s1.scatter(pts[:-1], [yy] * (len(pts) - 1), s=34, facecolor=BG, edgecolor=c, lw=1.6, zorder=3)
    s1.scatter(pts[-1:], [yy], s=80, color=c, zorder=4)
    s1.text(.075, yy, lab, family=MONO, fontsize=10.5, color=FG, ha="right", va="center", transform=s1.get_yaxis_transform())
s1.set_xlim(.08, .37); s1.set_ylim(-.6, len(rows) - .4)
s1.set_yticks([]); s1.set_xticks([.1, .2, .3]); s1.set_xticklabels(["10%", "20%", "30%"], family=MONO, fontsize=10, color=MUT)
for sp in ["top", "right", "left"]: s1.spines[sp].set_visible(False)
s1.spines["bottom"].set_color(EDGE); s1.tick_params(length=0); s1.grid(axis="x", color=EDGE, lw=.6, alpha=.6)
s1.text(.0, -.2, "open circle = lowest fifth, filled = highest", transform=s1.transAxes, family=MONO, fontsize=9.5, color=MUT)

s2 = fig.add_axes([.73, .125, .24, .13]); s2.set_facecolor(BG)
rws = R["bands"]["london"]["rows"]; mid = [362 if r["hi"] > 350 else (r["lo"] + r["hi"]) / 2 for r in rws]
s2.fill_between(mid, [r["riot_share"] for r in rws], color=FIRE, alpha=.18, lw=0)
s2.plot(mid, [r["riot_share"] for r in rws], color=FIRE, lw=2.2)
s2.plot(mid, [r["machine_share"] for r in rws], color=STEEL, lw=1.8)
s2.set_ylim(0, .3); s2.set_xlim(0, 370)
s2.set_yticks([0, .1, .2]); s2.set_yticklabels(["0%", "10%", "20%"], family=MONO, fontsize=10, color=MUT)
s2.set_xticks([0, 100, 200, 300]); s2.set_xticklabels(["0", "100", "200", "300 km"], family=MONO, fontsize=10, color=MUT)
for sp in ["top", "right"]: s2.spines[sp].set_visible(False)
for sp in ["left", "bottom"]: s2.spines[sp].set_color(EDGE)
s2.tick_params(length=0)
s2.text(0, 1.06, "Distance from London", transform=s2.transAxes, family=MONO, fontsize=10.5, color=FG)
s2.text(150, .215, "unrest", family=MONO, fontsize=10, color=FIRE); s2.text(240, .095, "machine", family=MONO, fontsize=10, color=STEEL)

# ---- take-away line
fig.text(.045, .074, "The riots did follow the machines, but most riots had no machine on record, enclosure barely matters, and poverty mattered a lot.",
         family=SER, fontsize=13.5, color=FG, style="italic")
# ---- footer
fig.text(.045, .012, "Data: Caprettini, B. and Voth, H.-J. 2020, Rage against the Machines, AER: Insights 2 (3), replication data doi.org/10.3886/E117044V1 (CC BY 4.0);\n"
         "riots from Holland (ed.) 2005, Swing Unmasked; machines from newspaper adverts and General Views of Agriculture (a sample, not a census).\n"
         "Main sample of 9,674 parishes for shares. Associations, not causes. Analysis and chart: Tristan Hotham, with Python and matplotlib.",
         family=MONO, fontsize=9, color=MUT, linespacing=1.5, va="bottom")
out = os.path.join(HERE, "captain_swing.png")
fig.savefig(out, dpi=200, facecolor=BG); print(out)
