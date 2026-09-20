#!/usr/bin/env python3
"""The stat panel: an interest radar and language meters, 8-bit.

LANGUAGES are real — the percentages are Gabriel's own, already published on his site
(70-Documents/Site/data.js). INTERESTS are a 0-5 self-assessment with no source in the
vault: they are PROPOSED and need his sign-off before this goes public.
"""
import font5x7 as F
from constellation8 import THEMES, BAYER, PX, snap

W, H = 1000, 400

# Gabriel's own numbers (2026-09-21). LIFE SCIENCES replaced a 'SEQUENCE' axis that described
# a method, not a domain; its value of 4 is mine, everything else is his. 0-5.
INTERESTS = [("BAYES", 4), ("LIFE SCIENCES", 4), ("NEURAL NETS", 4),
             ("SOFT. DEV", 3), ("LEARNING", 5), ("SYS DYNAMICS", 3)]
# REAL — from data.js
LANGS = [("SPANISH", "NATIVE", 100), ("ENGLISH", "C1", 85),
         ("FRENCH", "C1", 85), ("GERMAN", "A2", 30)]

CX, CY, R = 262, 220, 96
CELLS, CELLW = 16, 12


def hexpoint(i, r, n=6):
    import math
    a = -math.pi / 2 + i * 2 * math.pi / n
    return CX + r * math.cos(a), CY + r * math.sin(a)


def pixline(p, q):
    x1, y1 = p; x2, y2 = q
    n = max(abs(x2 - x1), abs(y2 - y1)) // PX
    seen = []
    for i in range(int(n) + 1):
        t = i / max(n, 1)
        c = (snap(x1 + (x2 - x1) * t), snap(y1 + (y2 - y1) * t))
        if c not in seen:
            seen.append(c)
    return seen


def polyfill(pts, dens):
    """Scanline fill on the pixel grid, dithered."""
    ys = [p[1] for p in pts]
    out = []
    for y in range(snap(min(ys)), snap(max(ys)) + PX, PX):
        xs = []
        for i in range(len(pts)):
            (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % len(pts)]
            if (y1 <= y < y2) or (y2 <= y < y1):
                xs.append(x1 + (y - y1) * (x2 - x1) / (y2 - y1))
        xs.sort()
        for a, b in zip(xs[::2], xs[1::2]):
            for x in range(snap(a), snap(b) + PX, PX):
                if BAYER[(y // PX) % 4][(x // PX) % 4] < dens:
                    out.append((x, y))
    return out


def build(theme):
    c = THEMES[theme]
    acc = c["clusters"]["bayes"]
    lang_col = c["clusters"]["learning"]
    buckets = {}

    def put(fill, op, x, y, w=PX, h=PX, z=1):
        buckets.setdefault((z, fill, op), []).append((x, y, w, h))

    def text(s, x, y, scale, col, anchor="start", z=3):
        for r in F.rects(s, x, y, scale, anchor):
            put(col, 1, *r, z=z)

    # ---- radar
    for ring in (0.2, 0.4, 0.6, 0.8, 1.0):
        pts = [hexpoint(i, R * ring) for i in range(6)]
        for i in range(6):
            for x, y in pixline(pts[i], pts[(i + 1) % 6]):
                put(c["faint"], .45 if ring < 1 else .8, x, y)
    for i in range(6):
        for x, y in pixline((CX, CY), hexpoint(i, R)):
            put(c["faint"], .35, x, y)

    data = [hexpoint(i, R * v / 5) for i, (_, v) in enumerate(INTERESTS)]
    for x, y in polyfill(data, 7):
        put(acc, .38, x, y, z=2)
    for i in range(6):
        for x, y in pixline(data[i], data[(i + 1) % 6]):
            put(acc, 1, x, y, z=2)
    for i, (label, v) in enumerate(INTERESTS):
        vx, vy = hexpoint(i, R * v / 5)
        put(acc, 1, snap(vx) - PX, snap(vy) - PX, 3 * PX, 3 * PX, z=3)
        lx, ly = hexpoint(i, R + 32)
        anchor = "middle" if i in (0, 3) else ("start" if lx > CX else "end")
        text(label, snap(lx), snap(ly) - 7, 2, c["soft"], anchor)

    # ---- language meters
    x0 = 560
    text("LANGUAGES", x0, 40, 2, lang_col)
    for row, (name, level, pct) in enumerate(LANGS):
        y = 96 + row * 46
        text(name, x0, y, 2, c["soft"])
        filled = round(pct / 100 * CELLS)
        for i in range(CELLS):
            col, op = (lang_col, 1) if i < filled else (c["faint"], .28)
            put(col, op, x0 + 144 + i * CELLW, y, 8, 14)
        text(level, x0 + 144 + CELLS * CELLW + 10, y, 2, c["faint"])

    text("INTERESTS", 60, 40, 2, acc)
    text("SELF-ASSESSED, 0-5", 60, 372, 2, c["faint"])
    text("AS PUBLISHED ON MY SITE", 560, 372, 2, c["faint"])

    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
         f'shape-rendering="crispEdges">',
         f'<rect width="{W}" height="{H}" fill="{c["paper"]}"/>']
    for (z, fill, op), rs in sorted(buckets.items(), key=lambda kv: kv[0][0]):
        a = f' fill="{fill}"' + (f' opacity="{op}"' if op != 1 else "")
        o.append(f"<g{a}>" + "".join(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}"/>' for x, y, w, h in rs) + "</g>")
    o.append("</svg>")
    return "\n".join(o)


if __name__ == "__main__":
    for t in THEMES:
        s = build(t)
        open(f"stats_{t}.svg", "w").write(s)
        print(f"stats_{t}.svg  {len(s)//1024} KB  {s.count('<rect')} rects")
