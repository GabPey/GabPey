#!/usr/bin/env python3
"""The concept constellation, 8-bit — generates dark_mode.svg and light_mode.svg.

Everything is a pixel block, including the text: a README image is loaded in an <img>, so a
pixel FONT would have to be installed on the viewer's machine to render. The 5x7 font in
font5x7.py is drawn as rects instead, which looks identical everywhere.

Edit NODES / EDGES / CLUSTERS below and re-run:  python3 constellation8.py
"""
import random
import font5x7 as F

PX = 4                      # one "pixel"
W, H = 1000, 620

def snap(v): return int(round(v / PX) * PX)

THEMES = {
 "dark": dict(paper="#06050f", d0="#0b0820", d1="#150d35", d2="#241657",
              ink="#f4f2ff", soft="#b9b2d8", faint="#6f6a90", star="#ffffff",
              clusters=dict(bayes="#9b6dff", neuro="#ffaa44", systems="#5fa8ff", learning="#3fd6a0"),
              fieldcol="#cfc9f0", edgeop=.78, fieldop=.55),
 "light": dict(paper="#f4f1e8", d0="#efebdf", d1="#e7e1d2", d2="#d9d2bf",
               ink="#14130f", soft="#46443e", faint="#8a857c", star="#14130f",
               clusters=dict(bayes="#5b34a8", neuro="#a3541a", systems="#2f5aa8", learning="#1f7a5e"),
               fieldcol="#8a857c", edgeop=.80, fieldop=.45),
}

# id: (x, y, LABEL, cluster)
NODES = {
 "vi":    (168, 236, "VARIATIONAL", "bayes"),
 "ssm":   (264, 320, "STATE-SPACE", "bayes"),
 "pp":    (128, 360, "PROBABILISTIC", "bayes"),
 "neu":   (836, 216, "NEUROSCIENCE", "neuro"),
 "dl":    (740, 296, "DEEP LEARNING", "neuro"),
 "phys":  (872, 344, "PHYSIOLOGY", "neuro"),
 "arch":  (252, 444, "ARCHITECTURE", "systems"),
 "pat":   (144, 496, "PATTERNS", "systems"),
 "rep":   (208, 552, "REPRODUCIBLE", "systems"),
 "assoc": (788, 444, "ASSOCIATION", "learning"),
 "org":   (884, 496, "ORGANIZATION", "learning"),
 "morph": (820, 552, "MORPHOLOGY", "learning"),
 "photosvi": (500, 224, "PHOTOSVI", None),
 "heart":    (500, 356, "THE HEART", None),
 "cove":     (500, 476, "COVE", None),
}
PROJ = {"photosvi", "heart", "cove"}

EDGES = [
 ("vi","ssm"),("ssm","pp"),("vi","pp"),
 ("neu","dl"),("dl","phys"),("neu","phys"),
 ("arch","pat"),("pat","rep"),("arch","rep"),
 ("assoc","org"),("org","morph"),("assoc","morph"),
 ("photosvi","vi"),("photosvi","ssm"),("photosvi","dl"),("photosvi","neu"),
 ("heart","ssm"),("heart","phys"),("heart","vi"),
 ("cove","arch"),("cove","pat"),("cove","assoc"),("cove","org"),("cove","morph"),
 ("photosvi","heart"),("heart","cove"),          # the spine
]

CLUSTERS = [(112, 188, "BAYES", "bayes", "start"),
            (888, 168, "NEURO / LIFE", "neuro", "end"),
            (104, 596, "SYSTEMS", "systems", "start"),
            (896, 596, "LEARNING", "learning", "end")]

BAYER = [[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]]

def line_blocks(a, b):
    """Pixel-stepped blocks from a to b, snapped to the grid."""
    x1, y1 = NODES[a][0], NODES[a][1]
    x2, y2 = NODES[b][0], NODES[b][1]
    n = max(abs(x2-x1), abs(y2-y1)) // PX
    seen, out = set(), []
    for i in range(n + 1):
        t = i / max(n, 1)
        p = (snap(x1 + (x2-x1)*t), snap(y1 + (y2-y1)*t))
        if p not in seen:
            seen.add(p); out.append(p)
    return out

def star_cells(big):
    """A little 8-bit star: diamond of cells, in grid units."""
    if big:
        return [(0,-2),(-1,-1),(0,-1),(1,-1),(-2,0),(-1,0),(0,0),(1,0),(2,0),
                (-1,1),(0,1),(1,1),(0,2)]
    return [(0,-1),(-1,0),(0,0),(1,0),(0,1)]

def build(theme):
    c = THEMES[theme]
    rnd = random.Random(11)
    buckets = {}                                  # (cls, fill, op) -> [(x,y,w,h)]

    def put(cls, fill, op, x, y, w=PX, h=PX, z=3):
        buckets.setdefault((z, cls, fill, op), []).append((x, y, w, h))

    def plate(label, cx, cy, scale, anchor="middle"):
        """A solid knock-out plate behind a label, so lines never cross the text."""
        w, h = F.width(label, scale), 7 * scale
        x = cx - w // 2 if anchor == "middle" else (cx - w if anchor == "end" else cx)
        put("", c["paper"], 1, x - PX, cy - PX, w + 2 * PX, h + 2 * PX, z=2)

    # --- pixel-dither glow, as patterns rather than tens of thousands of rects
    defs = []
    for i, (dens, col) in enumerate(((1, c["d0"]), (2, c["d0"]), (3, c["d1"]), (5, c["d1"]), (8, c["d2"]), (12, c["d2"]))):
        cells = "".join(
            f'<rect x="{x*PX}" y="{y*PX}" width="{PX}" height="{PX}"/>'
            for y in range(4) for x in range(4) if BAYER[y][x] < dens)
        defs.append(f'<pattern id="d{i}" width="{4*PX}" height="{4*PX}" patternUnits="userSpaceOnUse" '
                    f'fill="{col}">{cells}</pattern>')

    # --- lines, stars, glyphs
    for a, b in EDGES:
        cl = NODES[a][3] or NODES[b][3] or "bayes"
        col = c["star"] if (a in PROJ and b in PROJ) else c["clusters"].get(cl, c["soft"])
        for j, (x, y) in enumerate(line_blocks(a, b)):
            put(f"e{min(11, j//3)}", col, c["edgeop"], x, y, z=1)

    for i in range(150):
        put(f"t{i%6}", c["fieldcol"], round(rnd.uniform(.18, c["fieldop"]), 2),
            snap(rnd.uniform(0, W)), snap(rnd.uniform(0, H)), z=0)

    for k, (x, y, label, cl) in NODES.items():
        big = k in PROJ
        col = c["star"] if big else c["clusters"][cl]
        if big:
            for dy in range(-5, 6):
                for dx in range(-5, 6):
                    d = (dx * dx + dy * dy) ** .5
                    if 2.4 < d < 5.4 and BAYER[dy % 4][dx % 4] / 16 < (1 - d / 5.6) * .8:
                        put("", col, .22, x + dx * PX, y + dy * PX, z=1)
        for dx, dy in star_cells(big):
            put("b", col, 1, x + dx * PX, y + dy * PX, z=4)
        if big:
            tx, ty, sc, tc = x, y - 10 * PX, 3, c["ink"]
        else:
            tx, ty, sc, tc = x, y + 4 * PX, 2, c["soft"]
        plate(label, tx, ty, sc)
        for r in F.rects(label, tx, ty, sc, "middle"):
            put("", tc, 1, *r)

    for x, y, txt, cl, anch in CLUSTERS:
        plate(txt, x, y, 2, anch)
        for r in F.rects(txt, x, y, 2, anch):
            put("", c["clusters"][cl], 1, *r)

    for r in F.rects("GABRIEL PEYTRAL BORJA", 48, 44, 4):
        put("", c["ink"], 1, *r)
    for r in F.rects("COMPUTATIONAL AND MATHEMATICAL BIOLOGIST", 48, 88, 2):
        put("", c["clusters"]["bayes"], 1, *r)
    hook = "(I LIKE COMPUTERS, MATH AND LIFE SCIENCES.)"
    for r in F.rects(hook, 48, 114, 2):
        put("", c["soft"], 1, *r)
    put("cur", c["clusters"]["learning"], 1, 48 + F.width(hook, 2) + 8, 114, 2 * PX, 14)
    plate("YOUR CONCEPT NETWORK IS A CONSTELLATION", W // 2, 590, 2)
    for r in F.rects("YOUR CONCEPT NETWORK IS A CONSTELLATION", W // 2, 590, 2, "middle"):
        put("", c["faint"], 1, *r)

    # --- emit
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
         f'shape-rendering="crispEdges">', "<defs>" + "".join(defs) + "</defs>", "<style>",
         ".b{animation:bl 3.2s steps(2,end) infinite}@keyframes bl{0%,60%{opacity:1}61%,100%{opacity:.15}}",
         ".cur{animation:cu 1.1s steps(2,end) infinite}@keyframes cu{0%,50%{opacity:1}51%,100%{opacity:0}}",
         "@keyframes ap{to{opacity:inherit}}"]
    for i in range(12):
        o.append(f".e{i}{{animation:ap .18s steps(1,end) {0.3 + i * 0.11:.2f}s backwards}}")
    for i in range(6):
        o.append(f".t{i}{{animation:bl 3.2s steps(2,end) {i * 0.5:.1f}s infinite}}")
    o.append("@keyframes cu{0%,50%{opacity:1}51%,100%{opacity:0}}")
    o.append("@media (prefers-reduced-motion:reduce){*{animation:none!important}}")
    o.append("</style>")
    o.append(f'<rect width="{W}" height="{H}" fill="{c["paper"]}"/>')
    for i, r in enumerate((1010, 830, 650, 480, 320, 180)):
        o.append(f'<circle cx="200" cy="90" r="{r}" fill="url(#d{i})"/>')
    for (z, cls, fill, op), rs in sorted(buckets.items(), key=lambda kv: kv[0][0]):
        attrs = f' fill="{fill}"'
        if op != 1:
            attrs += f' opacity="{op}"'
        if cls:
            attrs += f' class="{cls}"'
        o.append(f"<g{attrs}>" + "".join(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}"/>' for x, y, w, h in rs) + "</g>")
    o.append("</svg>")
    return "\n".join(o)


for t in THEMES:
    s = build(t)
    open(f"{t}_mode.svg", "w").write(s)
    print(f"{t}_mode.svg  {len(s)//1024} KB  {s.count('<rect')} rects  {s.count('<g ')} groups")
