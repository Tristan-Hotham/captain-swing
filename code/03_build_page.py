"""Step 3: build ../index.html (and ../README.md) from page_template.html,
prose.html and README_template.md.

Every number in the text is a placeholder like {{counts.incidents_all|int}}
filled from ../data/results.json. The compact page data (../work/site.json)
is embedded as `const D = ...`.
Formats: int, pct0, pct1, pp1 (percentage points), f0, f1, f2, f3, words, raw.
Run: python3 03_build_page.py
"""
import os, re, json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
R = json.load(open(os.path.join(ROOT, "data", "results.json")))


def get(path):
    v = R
    for k in path.split("."):
        v = v[int(k)] if isinstance(v, list) else v[k]
    return v


def fmt(v, f):
    if f == "int": return f"{int(round(v)):,}"
    if f == "pct0": return f"{v * 100:.0f}%"
    if f == "pct1": return f"{v * 100:.1f}%"
    if f == "pp1": return f"{v * 100:.1f}"
    if f == "f0": return f"{v:.0f}"
    if f == "f1": return f"{v:.1f}"
    if f == "f2": return f"{v:.2f}"
    if f == "f3": return f"{v:.3f}"
    if f == "abs3": return f"{abs(v):.3f}"
    if f == "words":
        w = "zero one two three four five six seven eight nine ten eleven twelve".split()
        return w[int(v)] if int(v) < len(w) else f"{int(v):,}"
    return str(v)


def sub(m):
    path, _, f = m.group(1).partition("|")
    return fmt(get(path.strip()), f.strip() or "raw")


def fill(t):
    return re.sub(r"\{\{(.+?)\}\}", sub, t)


if __name__ == "__main__":
    site = json.load(open(os.path.join(ROOT, "work", "site.json")))
    t = open(os.path.join(HERE, "page_template.html")).read().replace("<!--PROSE-->", open(os.path.join(HERE, "prose.html")).read())
    t = fill(t)
    t = t.replace("/*DATA*/", "const D = " + json.dumps(site, separators=(",", ":"), ensure_ascii=False) + ";")
    open(os.path.join(ROOT, "index.html"), "w").write(t)
    print("index.html", len(t.encode()) // 1024, "KB")
    rt = os.path.join(HERE, "README_template.md")
    if os.path.exists(rt):
        open(os.path.join(ROOT, "README.md"), "w").write(fill(open(rt).read()))
        print("README.md written")
