"""Step 1: read the Caprettini and Voth (2020) replication package in place and
write small, reusable derived files.

Inputs (read in place, never copied): the openICPSR package E117044V1, at
SWING_DIR (default /home/claude/hist/_data11/swing):
  data/swing-cross.dta          parish cross-section (10,699 parishes of 1851)
  data/swing-panel.dta          parish x decade panel of unrest and threshers
  data/Parishes1851.shp/.dbf    1851 parish boundaries (British National Grid)
  data/EnglandWales.shp         outline of England and Wales
  rawdata/bna/thresh_ads.dta    threshing machines advertised in newspapers (dated)
  rawdata/gva/thresh_gva.dta    threshing machines in the General Views of Agriculture
  rawdata/gva/productivity.dta  29 machines with workers, bushels and hours
  rawdata/bna/Riots-pre1830.dta 679 dated episodes of unrest before 1830
  rawdata/bna/Newspapers.dta    60 newspaper towns (used for London's coordinates)

Outputs:
  data/parishes.csv             one row per parish: identifiers, centroid, riots, threshers, covariates
  data/machines.csv             every dated threshing machine record (year, parish, source, coordinates)
  data/unrest_pre1830.csv       every dated pre-1830 episode (year, month, day, parish, kind, coordinates)
  work/parish_shapes.json       simplified parish outlines, delta-encoded (for the page)
  work/outline.json             simplified England and Wales outline (for static maps)

Run: python3 01_prepare.py
"""
import os, struct, json
import numpy as np, pandas as pd
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union
from pyproj import Transformer

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
SW = os.environ.get("SWING_DIR", "/home/claude/hist/_data11/swing")
os.makedirs(os.path.join(ROOT, "work"), exist_ok=True)
TR = Transformer.from_crs(27700, 4326, always_xy=True)


def read_dbf(fn):
    b = open(fn, "rb").read()
    n, hl, rl = struct.unpack("<IHH", b[4:12])
    fields, i = [], 32
    while b[i] != 0x0D:
        fields.append((b[i:i + 11].split(b"\0")[0].decode(), chr(b[i + 11]), b[i + 16])); i += 32
    rows, off = [], hl
    for _ in range(n):
        rec = b[off:off + rl]; off += rl; p = 1; r = {}
        for name, t, ln in fields:
            v = rec[p:p + ln].decode("latin-1").strip(); p += ln
            r[name] = (float(v) if v not in ("", "*" * len(v)) else np.nan) if t in "NF" else v
        rows.append(r)
    return pd.DataFrame(rows)


def read_polys(fn):
    """Minimal ESRI shapefile reader for polygon (type 5) records."""
    b = open(fn, "rb").read(); off = 100; out = []
    while off < len(b):
        rn, cl = struct.unpack(">ii", b[off:off + 8]); off += 8
        rec = b[off:off + cl * 2]; off += cl * 2
        st = struct.unpack("<i", rec[:4])[0]
        if st == 0: out.append(None); continue
        npart, npt = struct.unpack("<ii", rec[36:44])
        parts = list(struct.unpack(f"<{npart}i", rec[44:44 + 4 * npart])) + [npt]
        pts = np.frombuffer(rec[44 + 4 * npart:44 + 4 * npart + 16 * npt], dtype="<f8").reshape(-1, 2)
        out.append([pts[parts[k]:parts[k + 1]] for k in range(npart)])
    return out


def rings_to_geom(rings):
    """Shapefile rings: clockwise = outer, counter-clockwise = hole."""
    polys = []
    for r in rings:
        if len(r) < 4: continue
        a = 0.5 * np.sum(r[:-1, 0] * r[1:, 1] - r[1:, 0] * r[:-1, 1])
        if a <= 0: polys.append([r, []])          # clockwise in shapefile = outer
        elif polys: polys[-1][1].append(r)
    g = [Polygon(o, h).buffer(0) for o, h in polys]
    g = [x for x in g if not x.is_empty]
    return unary_union(g) if g else None


# ---------- parish cross-section (their file, untouched values) ----------
cross = pd.read_stata(os.path.join(SW, "data", "swing-cross.dta"))
cross["REGION"] = cross["REGION"].astype(str)
cross["close"] = cross["close"].astype(str)

# ---------- parish boundaries: centroids and simplified outlines ----------
dbf = read_dbf(os.path.join(SW, "data", "Parishes1851.dbf"))
shp = read_polys(os.path.join(SW, "data", "Parishes1851.shp"))
assert len(dbf) == len(shp)
cx, cy, keep = [], [], []
shapes = {}
for i, rings in enumerate(shp):
    g = rings_to_geom(rings) if rings else None
    if g is None: cx.append(np.nan); cy.append(np.nan); continue
    c = g.centroid; cx.append(c.x); cy.append(c.y)
    shapes[i] = g
dbf["cx_bng"], dbf["cy_bng"] = cx, cy
dbf["PARISH_ID"] = dbf["PARISH_ID"].astype("Int64")
m = cross.merge(dbf[["GAZ_CNTY", "PARISH", "PARISH_ID", "cx_bng", "cy_bng"]].assign(shp_row=range(len(dbf))),
                on=["GAZ_CNTY", "PARISH", "PARISH_ID"], how="left", validate="1:1")
print("parishes", len(m), "matched to boundaries", m.cx_bng.notna().sum())
lon, lat = TR.transform(m.cx_bng.values, m.cy_bng.values)
m["lon"], m["lat"] = np.round(lon, 5), np.round(lat, 5)
# inside points (their LOGx_BNG / LATx_BNG are BNG eastings and northings guaranteed inside the parish)
ilon, ilat = TR.transform(m.LOGx_BNG.astype(float).values, m.LATx_BNG.astype(float).values)
m["in_lon"], m["in_lat"] = np.round(ilon, 5), np.round(ilat, 5)

# delta-encoded simplified outlines for the page: units of 0.001 degree
enc = []
for _, r in m.iterrows():
    g = shapes.get(r.shp_row) if pd.notna(r.shp_row) else None
    if g is None: enc.append(None); continue
    gs = g.simplify(180, preserve_topology=True)
    polys = [gs] if gs.geom_type == "Polygon" else list(getattr(gs, "geoms", []))
    rs = []
    for p in polys:
        if p.area < 40000 and len(polys) > 1: continue   # drop slivers and tiny islets
        x, y = p.exterior.coords.xy
        lo, la = TR.transform(np.array(x), np.array(y))
        q = np.round(np.c_[lo, la] * 1000).astype(int)
        q = q[np.r_[True, np.any(np.diff(q, axis=0) != 0, axis=1)]]
        if len(q) < 4: continue
        d = np.vstack([q[:1], np.diff(q, axis=0)]).ravel().tolist()
        rs.append(d)
    enc.append(rs or None)
m["shape"] = enc
json.dump(m["shape"].tolist(), open(os.path.join(ROOT, "work", "parish_shapes.json"), "w"), separators=(",", ":"))

# outline of England and Wales (their file), simplified, in BNG and WGS84
ew = read_polys(os.path.join(SW, "data", "EnglandWales.shp"))
og = unary_union([rings_to_geom(r) for r in ew if r]).simplify(400)
polys = [og] if og.geom_type == "Polygon" else list(og.geoms)
outline = []
for p in polys:
    if p.area < 2e6: continue
    x, y = p.exterior.coords.xy
    outline.append([[round(a), round(b)] for a, b in zip(x, y)])
json.dump({"crs": "EPSG:27700", "rings": outline}, open(os.path.join(ROOT, "work", "outline.json"), "w"), separators=(",", ":"))
print("outline rings", len(outline))

# ---------- dated threshing machines ----------
ads = pd.read_stata(os.path.join(SW, "rawdata", "bna", "thresh_ads.dta"))
gva = pd.read_stata(os.path.join(SW, "rawdata", "gva", "thresh_gva.dta"))
a = ads.assign(source="newspaper advert", n=ads.thresh_ads)[["year", "month", "day", "GAZ_CNTY", "PARISH", "newspaper", "source", "n"]]
g = gva.assign(source="General View of Agriculture (year approx. to decade)", n=gva.thresh_gva, month=np.nan, day=np.nan, newspaper="")[["year", "month", "day", "GAZ_CNTY", "PARISH", "newspaper", "source", "n"]]
mach = pd.concat([a, g], ignore_index=True)
mach["year"] = mach.year.astype(int)
loc = m[["GAZ_CNTY", "PARISH", "lat", "lon", "in_lat", "in_lon", "sample"]]
mach = mach.merge(loc, on=["GAZ_CNTY", "PARISH"], how="left")
mach.to_csv(os.path.join(ROOT, "data", "machines.csv"), index=False)
print("machine records", len(mach), "located", mach.lat.notna().sum())

# ---------- dated unrest before 1830 ----------
pre = pd.read_stata(os.path.join(SW, "rawdata", "bna", "Riots-pre1830.dta"))
pre["kind"] = np.where(pre.attacks.fillna(0) > 0, "attack on machines", np.where(pre.arsons.fillna(0) > 0, "arson", "other"))
pre["episodes"] = pre.attacks.fillna(0) + pre.arsons.fillna(0)
pre = pre.merge(loc, on=["GAZ_CNTY", "PARISH"], how="left")
pre[["year", "month", "day", "newspaper", "GAZ_CNTY", "PARISH", "kind", "episodes", "attacks", "arsons", "lat", "lon", "in_lat", "in_lon"]].to_csv(os.path.join(ROOT, "data", "unrest_pre1830.csv"), index=False)
print("pre-1830 episodes", len(pre), "located", pre.lat.notna().sum())

# ---------- parish table ----------
cols = ["GAZ_CNTY", "PARISH", "PARISH_ID", "REGION", "sample", "lat", "lon", "in_lat", "in_lon", "AREA_m2",
        "SWING", "SWING1", "BREAKTHRESH", "REST", "SWINGe", "thresh", "thresh1", "preriots",
        "density", "agri_share", "trade_share", "other_share", "sex_ratio", "urban",
        "distel", "distnews", "citynews", "distmanuf", "close", "heavysh", "cer", "enclosures", "low_enclosure",
        "GENER_P01", "POORRATE03", "POP01", "u_w", "u_s", "u_w_s", "whe_p", "oat_p", "MARKETTOWN",
        "dtmp1830au", "dpre1830sp", "dpre1830su"]
out = m[cols].copy()
news = pd.read_stata(os.path.join(SW, "rawdata", "bna", "Newspapers.dta"))
lon0, lat0 = [float(news.loc[news.NEWSCITY == "London", c].iloc[0]) for c in ["NEWSLOG", "NEWSLAT"]]


def hav(la1, lo1, la2, lo2):
    la1, lo1, la2, lo2 = map(np.radians, [la1, lo1, la2, lo2])
    h = np.sin((la2 - la1) / 2) ** 2 + np.cos(la1) * np.cos(la2) * np.sin((lo2 - lo1) / 2) ** 2
    return 2 * 6371.0 * np.arcsin(np.sqrt(h))


# distance to London from their WGS84 centroid (same point they use for Elham)
out["dist_london_km"] = np.round(hav(cross.LATo_WGS84.astype(float), cross.LOGo_WGS84.astype(float), lat0, lon0), 2)
out["london_lat"], out["london_lon"] = lat0, lon0
out.to_csv(os.path.join(ROOT, "data", "parishes.csv"), index=False)
print("parishes.csv", len(out))

prod = pd.read_stata(os.path.join(SW, "rawdata", "gva", "productivity.dta"))
prod.to_csv(os.path.join(ROOT, "work", "productivity.csv"), index=False)
panel = pd.read_stata(os.path.join(SW, "data", "swing-panel.dta"), columns=["period", "sample", "riots", "GAZ_CNTY", "PARISH"])
panel.to_csv(os.path.join(ROOT, "work", "panel_small.csv"), index=False)
