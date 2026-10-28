"""Step 4: render ../header.png (1200x630 social card) with Playwright Chromium.

Fonts: FONT_DIR with FrauncesVar.ttf, SourceSerif4-Regular.ttf, IBMPlexMono-Regular.ttf
and IBMPlexMono-Medium.ttf; otherwise system serif fonts are used.
Run: python3 04_header.py
"""
import os, json, math
import pandas as pd
from pyproj import Transformer
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
R = json.load(open(os.path.join(ROOT, "data", "results.json")))
FD = os.environ.get("FONT_DIR", "/tmp/claude-0/-home-claude/c232619d-81e0-53f3-9de6-41e973630753/scratchpad/fonts")
OL = json.load(open(os.path.join(ROOT, "work", "outline.json")))["rings"]
p = pd.read_csv(os.path.join(ROOT, "data", "parishes.csv"))
m = pd.read_csv(os.path.join(ROOT, "data", "machines.csv"))
TR = Transformer.from_crs(4326, 27700, always_xy=True)
p["x"], p["y"] = TR.transform(p.in_lon.values, p.in_lat.values)
m["x"], m["y"] = TR.transform(m.in_lon.values, m.in_lat.values)
X0, X1, Y0, Y1 = 130000, 660000, 0, 660000
H = 600; W = H * (X1 - X0) / (Y1 - Y0)
px = lambda x, y: ((x - X0) / (X1 - X0) * W, (Y1 - y) / (Y1 - Y0) * H)
land = "".join("M" + "L".join(f"{px(a, b)[0]:.1f} {px(a, b)[1]:.1f}" for a, b in r) + "Z" for r in OL)
r = p[p.SWING > 0]
dots = "".join(f'<circle cx="{px(a, b)[0]:.1f}" cy="{px(a, b)[1]:.1f}" r="{1.2 + math.sqrt(n) * 1.25:.2f}"/>' for a, b, n in zip(r.x, r.y, r.SWING))
md = "".join(f'<rect x="{px(a, b)[0] - 1.6:.1f}" y="{px(a, b)[1] - 1.6:.1f}" width="3.2" height="3.2"/>' for a, b in zip(m.x, m.y) if a == a)
ff = ""
if os.path.isdir(FD):
    ff = "".join(f"@font-face{{font-family:'{n}';src:url('file://{FD}/{f}');font-weight:{w};}}" for n, f, w in [
        ("Fraunces", "FrauncesVar.ttf", "100 900"), ("Source Serif 4", "SourceSerif4-Regular.ttf", "400"),
        ("IBM Plex Mono", "IBMPlexMono-Regular.ttf", "400"), ("IBM Plex Mono", "IBMPlexMono-Medium.ttf", "500")])
M = R["machines"]
html = f"""<!doctype html><html><head><meta charset="utf-8"><style>{ff}
body{{margin:0;width:1200px;height:630px;background:#F3EEE1;color:#211F1A;overflow:hidden;position:relative;font-family:'Source Serif 4',Georgia,serif}}
.k{{position:absolute;left:64px;top:58px;font:500 15px/1 'IBM Plex Mono',monospace;letter-spacing:.14em;text-transform:uppercase;color:#6A6458;display:flex;gap:12px;align-items:center}}
.k b{{background:#C2410C;color:#fff;padding:7px 9px;font-weight:500}}
.o{{position:absolute;left:64px;top:104px;font:600 38px/1 Fraunces,Georgia,serif;color:#C2410C}}
h1{{position:absolute;left:60px;top:150px;margin:0;font:900 82px/.92 Fraunces,Georgia,serif;letter-spacing:-.02em;font-variation-settings:"SOFT" 50;width:700px}}
h1 i{{font-style:normal;color:#35576E}} h1 em{{font-style:normal;color:#C2410C}}
p{{position:absolute;left:64px;top:345px;width:600px;margin:0;font-size:25px;line-height:1.36;color:#3A3730}}
.f{{position:absolute;left:64px;bottom:40px;font:400 14px/1 'IBM Plex Mono',monospace;letter-spacing:.1em;text-transform:uppercase;color:#7D776B}}
.map{{position:absolute;right:30px;top:15px}}
.lg{{position:absolute;right:46px;bottom:28px;font:400 13px/1.5 'IBM Plex Mono',monospace;color:#6A6458;text-align:right}}
.lg i{{display:inline-block;width:10px;height:10px;margin-right:6px;vertical-align:-1px}}
</style></head><body>
<div class="k"><b>Data study</b><span>History × technology · 1830</span></div>
<div class="o">Captain Swing:</div>
<h1>did the <em>riots</em> follow the <i>machines</i>?</h1>
<p>{R['counts']['incidents_all']:,} incidents in {R['counts']['parishes_all']:,} parishes. With a recorded threshing machine, {M['riot_share_with'] * 100:.0f}% rioted; without, {M['riot_share_without'] * 100:.0f}%.</p>
<div class="f">Dr Tristan Hotham · Data: Caprettini and Voth 2020</div>
<svg class="map" width="{W:.0f}" height="{H}" viewBox="0 0 {W:.0f} {H}"><path d="{land}" fill="#E7DFCB" stroke="#CDBF9F" stroke-width="1"/>
<g fill="#C2410C" fill-opacity=".45" stroke="#C2410C" stroke-width=".5">{dots}</g><g fill="#35576E">{md}</g></svg>
<div class="lg"><i style="background:#C2410C;opacity:.6;border-radius:50%"></i>Swing unrest<br><i style="background:#35576E"></i>Recorded machine</div>
</body></html>"""
tmp = os.path.join(ROOT, "work", "header.html"); open(tmp, "w").write(html)
with sync_playwright() as pw:
    b = pw.chromium.launch(); pg = b.new_page(viewport={"width": 1200, "height": 630})
    pg.goto("file://" + os.path.abspath(tmp)); pg.wait_for_timeout(700)
    pg.screenshot(path=os.path.join(ROOT, "header.png")); b.close()
os.remove(tmp)
print("header.png written")
