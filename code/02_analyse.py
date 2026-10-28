"""Step 2: descriptive analysis. Writes data/results.json (every number used on the
page, in the paper, the blog and the collage), data/counties.csv, data/bands.csv
and work/site.json (compact data for the page).

Two kinds of result are kept apart in results.json:
  repro.*  : checks that I reproduce Caprettini and Voth's published descriptive
             statistics and two of their regression coefficients from their data.
             These are THEIR results; I only re-run them.
  everything else: my own descriptive analysis of their open data.

Run: python3 02_analyse.py
"""
import os, json, math
import numpy as np, pandas as pd
import statsmodels.formula.api as smf
from scipy.spatial import cKDTree
from scipy import stats
from pyproj import Transformer

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
D = os.path.join(ROOT, "data"); W = os.path.join(ROOT, "work")
p = pd.read_csv(os.path.join(D, "parishes.csv"))
mach = pd.read_csv(os.path.join(D, "machines.csv"))
pre = pd.read_csv(os.path.join(D, "unrest_pre1830.csv"))
panel = pd.read_csv(os.path.join(W, "panel_small.csv"))
prod = pd.read_csv(os.path.join(W, "productivity.csv"))
R = {}
rnd = lambda x, d=4: None if x is None or (isinstance(x, float) and math.isnan(x)) else round(float(x), d)

with np.errstate(divide="ignore"):
    p["log_density"] = np.log(p.density)
p["log_sex_ratio"] = np.log(p.sex_ratio)
p["log_distel"] = np.log(p.distel)
p["log_distnews"] = np.log(p.distnews)
p["log_dist_london"] = np.log(p.dist_london_km.clip(lower=1))
s = p[p["sample"] == 1].copy()

# ---------------- counts ----------------
R["counts"] = dict(
    parishes_all=int(len(p)), parishes_sample=int(len(s)),
    incidents_all=int(p.SWING.sum()), incidents_sample=int(s.SWING.sum()),
    machine_attacks_all=int(p.BREAKTHRESH.sum()), machine_attacks_sample=int(s.BREAKTHRESH.sum()),
    other_incidents_all=int(p.REST.sum()),
    riot_parishes_all=int((p.SWING > 0).sum()), riot_parishes_sample=int((s.SWING > 0).sum()),
    riot_parish_share_sample=rnd((s.SWING > 0).mean()),
    machines_all=int(p.thresh.sum()), machines_sample=int(s.thresh.sum()),
    machine_parishes_all=int((p.thresh > 0).sum()), machine_parishes_sample=int((s.thresh > 0).sum()),
    machine_parish_share_sample=rnd((s.thresh > 0).mean()),
    machine_records=int(len(mach)), machine_records_ads=int((mach.source == "newspaper advert").sum()),
    machine_records_gva=int((mach.source != "newspaper advert").sum()),
    pre1830_episodes=int(len(pre)), pre1830_attacks=int(pre.attacks.fillna(0).sum()), pre1830_arsons=int(pre.arsons.fillna(0).sum()),
    pre1830_first_year=int(pre.year.min()), pre1830_last_year=int(pre.year.max()),
    incidents_to_april_1831_all=int(p.SWINGe.sum()),
    attack_share_of_incidents=rnd(p.BREAKTHRESH.sum() / p.SWING.sum()),
    max_incidents_parish=int(p.SWING.max()),
)
top = p.sort_values("SWING", ascending=False).head(8)
R["top_parishes"] = [dict(parish=r.PARISH.title(), county=r.GAZ_CNTY.title(), incidents=int(r.SWING), machines=int(r.thresh)) for r in top.itertuples()]

# ---------------- reproduction of their published numbers (THEIRS) ----------------
pub = dict(n=9674, preriots=0.067, swing=0.308, thresh=0.062, ols1_thresh=0.389, ols1_se=0.071, iv7_thresh=6.361, iv7_se=1.616,
           fs_heavy=-0.034, rf_heavy=-0.218, period_means=[0.001, 0.001, 0.009, 0.055, 0.176])
ols = smf.ols("SWING ~ thresh + log_density + agri_share + log_sex_ratio + log_distel + log_distnews", data=s).fit(cov_type="HC1")
ctrl = "cer + log_density + agri_share + log_sex_ratio + log_distel + log_distnews"
fs = smf.ols(f"thresh ~ heavysh + {ctrl}", data=s).fit(cov_type="HC1")
rf = smf.ols(f"SWING ~ heavysh + {ctrl}", data=s).fit(cov_type="HC1")
# 2SLS by hand: point estimate and heteroskedasticity-robust (HC0) standard error
ss = s.dropna(subset=["SWING", "thresh", "heavysh", "cer", "log_density", "agri_share", "log_sex_ratio", "log_distel", "log_distnews"])
Xc = np.c_[np.ones(len(ss)), ss[["cer", "log_density", "agri_share", "log_sex_ratio", "log_distel", "log_distnews"]].values]
X = np.c_[ss.thresh.values, Xc]; Z = np.c_[ss.heavysh.values, Xc]; y = ss.SWING.values
Pz = Z @ np.linalg.solve(Z.T @ Z, Z.T @ X)
b = np.linalg.solve(Pz.T @ X, Pz.T @ y); e = y - X @ b
A = np.linalg.inv(Pz.T @ Pz); V = A @ (Pz.T * e ** 2) @ Pz @ A
pm = panel[panel["sample"] == 1].groupby("period").riots.mean()
R["repro"] = dict(published=pub, n=int(len(s)), preriots=rnd(s.preriots.mean(), 3), swing=rnd(s.SWING.mean(), 3), thresh=rnd(s.thresh.mean(), 3),
                  ols1_thresh=rnd(ols.params["thresh"], 3), ols1_se=rnd(ols.bse["thresh"], 3),
                  fs_heavy=rnd(fs.params["heavysh"], 3), rf_heavy=rnd(rf.params["heavysh"], 3),
                  iv7_thresh=rnd(b[0], 3), iv7_se=rnd(math.sqrt(V[0, 0]), 3), iv_n=int(len(ss)),
                  period_means=[rnd(pm.get(k, np.nan), 3) for k in [1, 2, 3, 4, 5]])
print("repro", R["repro"])

# ---------------- machines and riots (MINE) ----------------
def share(q, col="SWING"): return rnd((q[col] > 0).mean())
m1, m0 = s[s.thresh > 0], s[s.thresh == 0]
R["machines"] = dict(
    riot_share_with=share(m1), riot_share_without=share(m0), ratio=rnd(share(m1) / share(m0), 2),
    n_with=int(len(m1)), n_without=int(len(m0)),
    incidents_mean_with=rnd(m1.SWING.mean(), 3), incidents_mean_without=rnd(m0.SWING.mean(), 3),
    attack_share_with=share(m1, "BREAKTHRESH"), attack_share_without=share(m0, "BREAKTHRESH"),
    attack_ratio=rnd(share(m1, "BREAKTHRESH") / share(m0, "BREAKTHRESH"), 2),
    other_share_with=share(m1, "REST"), other_share_without=share(m0, "REST"),
    riot_parishes_with_machine=int(((s.SWING > 0) & (s.thresh > 0)).sum()),
    riot_parishes_without_machine=int(((s.SWING > 0) & (s.thresh == 0)).sum()),
    riot_parishes_without_machine_share=rnd(((s.SWING > 0) & (s.thresh == 0)).sum() / (s.SWING > 0).sum()),
    machine_parishes_quiet_share=rnd((m1.SWING == 0).mean()),
)
# by number of machines
bym = []
for lab, q in [("0", s[s.thresh == 0]), ("1", s[s.thresh == 1]), ("2 or more", s[s.thresh >= 2])]:
    bym.append(dict(label=lab, n=int(len(q)), riot_share=share(q), incidents_mean=rnd(q.SWING.mean(), 3)))
R["machines"]["by_count"] = bym
# within region
reg = []
for g, q in s.groupby("REGION"):
    a1, a0 = q[q.thresh > 0], q[q.thresh == 0]
    reg.append(dict(region=g, n=int(len(q)), n_with=int(len(a1)), riot_share_with=share(a1), riot_share_without=share(a0),
                    incidents=int(q.SWING.sum()), machines=int(q.thresh.sum()), riot_share=share(q)))
reg.sort(key=lambda r: -r["riot_share"])
R["regions"] = reg
R["machines"]["regions_higher_with"] = int(sum(r["riot_share_with"] > r["riot_share_without"] for r in reg))
# neighbour comparison: each machine parish against machine-free parishes within 10 km
TB = Transformer.from_crs(4326, 27700, always_xy=True)
s["x"], s["y"] = TB.transform(s.in_lon.values, s.in_lat.values)
tree = cKDTree(s[s.thresh == 0][["x", "y"]].values); nb = s[s.thresh == 0].reset_index(drop=True)
diffs, nbs = [], []
for r in s[s.thresh > 0].itertuples():
    idx = tree.query_ball_point([r.x, r.y], 10000)
    if not idx: continue
    nbr = (nb.loc[idx, "SWING"] > 0).mean(); nbs.append(nbr); diffs.append(float(r.SWING > 0) - nbr)
diffs = np.array(diffs)
rng = np.random.default_rng(1830)
boot = [rng.choice(diffs, len(diffs)).mean() for _ in range(4000)]
R["neighbours"] = dict(radius_km=10, n_pairs=int(len(diffs)), machine_riot_share=rnd(np.mean(np.array(nbs) + diffs)),
                       neighbour_riot_share=rnd(np.mean(nbs)), diff=rnd(diffs.mean()), ci_lo=rnd(np.percentile(boot, 2.5)), ci_hi=rnd(np.percentile(boot, 97.5)),
                       mean_neighbours=rnd(np.mean([len(tree.query_ball_point([r.x, r.y], 10000)) for r in s[s.thresh > 0].itertuples()]), 1))

# ---------------- rival explanations: gradients across quintiles (MINE) ----------------
def gradient(col, label, unit, q=5, sub=None, note=""):
    d = (sub if sub is not None else s).dropna(subset=[col]).copy()
    d["g"] = pd.qcut(d[col].rank(method="first"), q, labels=False)
    rows = []
    for k, gq in d.groupby("g"):
        rows.append(dict(q=int(k) + 1, lo=rnd(gq[col].min(), 3), hi=rnd(gq[col].max(), 3), mean=rnd(gq[col].mean(), 3), n=int(len(gq)),
                         riot_share=share(gq), machine_share=share(gq, "thresh"), incidents_mean=rnd(gq.SWING.mean(), 3)))
    rho, pv = stats.spearmanr(d[col], d.SWING)
    rho1, pv1 = stats.spearmanr(d[col], (d.SWING > 0).astype(int))
    return dict(key=col, label=label, unit=unit, n=int(len(d)), quantiles=q, rows=rows, note=note,
                top_minus_bottom=rnd(rows[-1]["riot_share"] - rows[0]["riot_share"]), spearman=rnd(rho, 3), spearman_p=rnd(pv, 4),
                spearman_any=rnd(rho1, 3), spearman_any_p=rnd(pv1, 4), coverage=rnd(len(d) / len(s), 3))

G = {}
G["enclosures"] = gradient("enclosures", "Common land enclosed by 1820 (district)", "%", note="District estimate from Gonner (1912), only districts he covers")
G["poor"] = gradient("GENER_P01", "Poor rates per head, 1801", "", note="Only parishes answering the 1834 Poor Law inquiry")
G["unemp"] = gradient("u_w", "Winter unemployment among farm workers, 1834", "%", q=4, note="Reported in 1834, after the riots; only parishes that answered")
G["wheat"] = gradient("whe_p", "Average wheat price at the nearest market, 1820s", "", note="Market-town price, shared by all parishes near that market")
G["agri"] = gradient("agri_share", "Share of workers in agriculture, 1801", "%")
G["heavy"] = gradient("heavysh", "Share of the parish on heavy clay soil", "%", note="Caprettini and Voth's instrument: heavy soils suited threshing machines less")
G["machines_dens"] = None
del G["machines_dens"]
R["gradients"] = G
R["machines"]["gap"] = rnd(R["machines"]["riot_share_with"] - R["machines"]["riot_share_without"])

# distance bands
def bands(col, edges, label):
    d = s.copy(); d["b"] = pd.cut(d[col], edges)
    out = []
    for k, q in d.groupby("b", observed=True):
        out.append(dict(lo=int(k.left), hi=int(k.right), n=int(len(q)), riot_share=share(q), machine_share=share(q, "thresh"), incidents_mean=rnd(q.SWING.mean(), 3)))
    return dict(label=label, rows=out)
R["bands"] = dict(london=bands("dist_london_km", list(range(0, 351, 25)) + [600], "Distance from London (km)"),
                  elham=bands("distel", list(range(0, 351, 25)) + [600], "Distance from Elham, Kent (km)"))
pd.DataFrame([dict(kind=k, **r) for k in ["london", "elham"] for r in R["bands"][k]["rows"]]).to_csv(os.path.join(D, "bands.csv"), index=False)
lb = R["bands"]["london"]["rows"]
R["london"] = dict(within100_share=rnd((s[s.dist_london_km <= 100].SWING > 0).mean()), beyond200_share=rnd((s[s.dist_london_km > 200].SWING > 0).mean()),
                   within100_n=int((s.dist_london_km <= 100).sum()), beyond200_n=int((s.dist_london_km > 200).sum()),
                   within150_incident_share=rnd(s[s.dist_london_km <= 150].SWING.sum() / s.SWING.sum()),
                   within150_parish_share=rnd((s.dist_london_km <= 150).mean()),
                   peak_band=max(lb, key=lambda r: r["riot_share"]))
R["elham"] = dict(within50_share=rnd((s[s.distel <= 50].SWING > 0).mean()), within50_n=int((s.distel <= 50).sum()),
                  within50_incidents_mean=rnd(s[s.distel <= 50].SWING.mean(), 3))

# outside options: machine gap near and far from industrial towns (cf. their Figure 3)
oo = {}
for c in ["Close", "Distant"]:
    q = s[s.close == c]; a1, a0 = q[q.thresh > 0], q[q.thresh == 0]
    oo[c.lower()] = dict(n=int(len(q)), n_with=int(len(a1)), with_share=share(a1), without_share=share(a0), gap=rnd(share(a1) - share(a0)),
                         incidents_with=rnd(a1.SWING.mean(), 3), incidents_without=rnd(a0.SWING.mean(), 3))
oo["median_km"] = rnd(s.distmanuf.median(), 1)
oo["median_km_all"] = rnd(p.distmanuf.median(), 1)
oo["close_max_km"] = rnd(s[s.close == "Close"].distmanuf.max(), 1)
R["outside"] = oo
# enclosure split by their low/high flag
R["enclosure_split"] = {k: dict(n=int(len(q)), riot_share=share(q), incidents_mean=rnd(q.SWING.mean(), 3)) for k, q in
                        [("low", s[s.low_enclosure == 1]), ("high", s[s.low_enclosure == 0])]}

# ---------------- my linear probability models (MINE) ----------------
def lpm(formula, data, name):
    d = data.dropna(subset=[c for c in ["SWING", "thresh", "log_density", "agri_share", "log_dist_london", "enclosures", "GENER_P01", "u_w"] if c in formula])
    f = smf.ols(formula, data=d).fit(cov_type="HC1")
    terms = {}
    for t in f.params.index:
        if t.startswith("C(") or t == "Intercept": continue
        sd = d[t].std() if t in d else 1.0
        terms[t] = dict(b=rnd(f.params[t], 4), se=rnd(f.bse[t], 4), p=rnd(f.pvalues[t], 4), sd=rnd(sd, 4), b_sd=rnd(f.params[t] * sd, 4))
    return dict(name=name, n=int(f.nobs), r2=rnd(f.rsquared, 3), mean_y=rnd((d.SWING > 0).mean(), 4), terms=terms)

s["any"] = (s.SWING > 0).astype(int); s["machine"] = (s.thresh > 0).astype(int)
base = "any ~ machine + log_dist_london + log_density + agri_share + C(REGION)"
R["models"] = [lpm(base, s, "All parishes"),
               lpm(base + " + enclosures", s, "With enclosure"),
               lpm(base + " + GENER_P01", s, "With poor rates"),
               lpm(base + " + u_w", s, "With 1834 winter unemployment")]
for mdl in R["models"]: print(mdl["name"], mdl["n"], {k: (v["b"], v["se"]) for k, v in mdl["terms"].items()})

# ---------------- timelines ----------------
yrs = list(range(1800, 1831))
mby = mach.groupby("year").n.sum()
R["timeline"] = dict(years=yrs, machines=[int(mby.get(y, 0)) for y in yrs],
                     machines_ads=[int(mach[(mach.source == "newspaper advert") & (mach.year == y)].n.sum()) for y in yrs],
                     cum=[int(mby[mby.index <= y].sum()) for y in yrs])
py = list(range(1790, 1830)); pby = pre.groupby("year").episodes.sum()
R["timeline"]["pre_years"] = py
R["timeline"]["pre"] = [int(pby.get(y, 0)) for y in py]
R["timeline"]["pre_before1790"] = int(pre[pre.year < 1790].episodes.sum())
R["timeline"]["pre_1820s"] = int(pre[(pre.year >= 1820)].episodes.sum())
R["timeline"]["pre_1820s_share"] = rnd(pre[(pre.year >= 1820)].episodes.sum() / pre.episodes.sum())
R["timeline"]["pre_peak_year"] = int(pby.idxmax()); R["timeline"]["pre_peak"] = int(pby.max())
R["timeline"]["machine_peak_year"] = int(mby.idxmax()); R["timeline"]["machine_peak"] = int(mby.max())
R["timeline"]["machines_by_decade"] = {f"{d}s": int(mach[(mach.year >= d) & (mach.year < d + 10)].n.sum()) for d in [1800, 1810, 1820]}
R["timeline"]["machines_1830"] = int(mach[mach.year == 1830].n.sum())
R["timeline"]["decade_labels"] = ["before 1800", "1800s", "1810s", "1820s", "1830 to 1832"]
R["timeline"]["decade_ratio_1830_1820"] = rnd(R["repro"]["period_means"][4] / R["repro"]["period_means"][3], 2)

# ---------------- counties ----------------
cty = s.groupby("GAZ_CNTY").agg(parishes=("PARISH", "size"), incidents=("SWING", "sum"), riot_parishes=("SWING", lambda x: int((x > 0).sum())),
                                 attacks=("BREAKTHRESH", "sum"), machines=("thresh", "sum"), machine_parishes=("thresh", lambda x: int((x > 0).sum())),
                                 region=("REGION", lambda x: x.mode().iloc[0])).reset_index()
cty["riot_share"] = (cty.riot_parishes / cty.parishes).round(4)
cty["machines_per100"] = (cty.machines / cty.parishes * 100).round(3)
cty["incidents_per100"] = (cty.incidents / cty.parishes * 100).round(3)
cty["county"] = cty.GAZ_CNTY.str.title()
cty = cty.sort_values("incidents", ascending=False)
cty.drop(columns="GAZ_CNTY").to_csv(os.path.join(D, "counties.csv"), index=False)
big = cty[cty.parishes >= 40]
rho, pv = stats.spearmanr(big.machines_per100, big.riot_share)
R["counties"] = dict(n=int(len(cty)), n_big=int(len(big)), spearman=rnd(rho, 3), spearman_p=rnd(pv, 5),
                     top=[dict(county=r.county, parishes=int(r.parishes), incidents=int(r.incidents), riot_share=rnd(r.riot_share), machines=int(r.machines),
                               machines_per100=rnd(r.machines_per100, 2)) for r in cty.head(10).itertuples()],
                     top5_incident_share=rnd(cty.head(5).incidents.sum() / cty.incidents.sum()),
                     rows=[dict(county=r.county, region=r.region, parishes=int(r.parishes), incidents=int(r.incidents), riot_share=rnd(r.riot_share),
                                machines=int(r.machines), machines_per100=rnd(r.machines_per100, 2), attacks=int(r.attacks)) for r in cty.itertuples()])

# ---------------- productivity (their data and their flail benchmark) ----------------
prod["l"] = prod.men + 0.5 * (prod.women + prod.boys + prod.girls)
prod["prod"] = prod.bushels / prod.hours / prod.l
pp = {k: dict(n=int(len(q)), mean=rnd(q["prod"].mean(), 2), median=rnd(q["prod"].median(), 2)) for k, q in prod.groupby("power")}
R["productivity"] = dict(flail=0.4, by_power=pp, horses_ratio=rnd(pp["horses"]["mean"] / 0.4, 1), horses_median_ratio=rnd(pp["horses"]["median"] / 0.4, 1),
                         n=int(len(prod)), note="Bushels threshed per worker-hour; women and children count as half a man, as in Caprettini and Voth's appendix code; flail benchmark 0.4 from their code (citing Gregory Clark).")
R["productivity"]["rows"] = [dict(power=r.power, bushels_per_worker_hour=rnd(r.prod, 2)) for r in prod.itertuples()]

# ---------------- context facts from Wikipedia (sourced, not computed) ----------------
R["context"] = dict(source="Wikipedia, 'Swing Riots' and 'Threshing machine' (CC BY-SA 4.0), retrieved 28 October 2026",
                    first_machine_date="28 August 1830", first_machine_place="Lower Hardres, Kent",
                    tried=2000, death_sentences=252, hanged=19, imprisoned=644, transported=481,
                    threshing_labour_share="about one quarter")

# ---------------- page data ----------------
sorted_cty = sorted(p.GAZ_CNTY.unique()); ci = {c: i for i, c in enumerate(sorted_cty)}
regs = sorted(p.REGION.unique()); ri = {c: i for i, c in enumerate(regs)}
shapes = json.load(open(os.path.join(W, "parish_shapes.json")))
f = lambda v, d=2: None if pd.isna(v) else round(float(v), d)
par = []
for i, r in enumerate(p.itertuples()):
    par.append([f(r.in_lat, 4), f(r.in_lon, 4), int(r.SWING), int(r.BREAKTHRESH), int(r.thresh), f(r.enclosures, 1), f(r.GENER_P01, 2),
                f(r.u_w, 3), int(round(r.dist_london_km)), ci[r.GAZ_CNTY], r.PARISH.title(), ri[r.REGION], int(r.sample), f(r.heavysh, 2), int(round(r.distel))])
site = dict(R=R, counties=[c.title() for c in sorted_cty], regions=regs,
            cols=["lat", "lon", "swing", "attacks", "machines", "enclosures", "poor", "unemp", "dlondon", "county", "name", "region", "sample", "heavy", "delham"],
            par=par, shapes=shapes,
            mach=[[f(r.in_lat, 4), f(r.in_lon, 4), int(r.year), int(r.n), 0 if r.source == "newspaper advert" else 1, r.PARISH.title()] for r in mach.itertuples()],
            pre=[[f(r.in_lat, 4), f(r.in_lon, 4), int(r.year), 0 if r.kind == "arson" else 1, int(r.episodes), r.PARISH.title()] for r in pre.itertuples()],
            london=[float(p.london_lat.iloc[0]), float(p.london_lon.iloc[0])])
json.dump(site, open(os.path.join(W, "site.json"), "w"), separators=(",", ":"), ensure_ascii=False)
json.dump(R, open(os.path.join(D, "results.json"), "w"), indent=1, ensure_ascii=False)
print(json.dumps({k: R[k] for k in ["counts", "machines", "neighbours", "london", "elham", "outside", "productivity", "counties"]}, indent=0)[:6000])
for k, g in G.items(): print(k, g["n"], g["top_minus_bottom"], g["spearman_any"], [r["riot_share"] for r in g["rows"]])
