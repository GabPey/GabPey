"""A 5x7 bitmap font, written as explicit rows so a malformed glyph fails loudly."""
F = """
A .###. #...# #...# ##### #...# #...# #...#
B ####. #...# #...# ####. #...# #...# ####.
C .###. #...# #.... #.... #.... #...# .###.
D ####. #...# #...# #...# #...# #...# ####.
E ##### #.... #.... ####. #.... #.... #####
F ##### #.... #.... ####. #.... #.... #....
G .###. #...# #.... #.### #...# #...# .###.
H #...# #...# #...# ##### #...# #...# #...#
I ##### ..#.. ..#.. ..#.. ..#.. ..#.. #####
J ..### ...#. ...#. ...#. ...#. #..#. .##..
K #...# #..#. #.#.. ##... #.#.. #..#. #...#
L #.... #.... #.... #.... #.... #.... #####
M #...# ##.## #.#.# #...# #...# #...# #...#
N #...# ##..# #.#.# #..## #...# #...# #...#
O .###. #...# #...# #...# #...# #...# .###.
P ####. #...# #...# ####. #.... #.... #....
Q .###. #...# #...# #...# #.#.# #..#. .##.#
R ####. #...# #...# ####. #.#.. #..#. #...#
S .#### #.... #.... .###. ....# ....# ####.
T ##### ..#.. ..#.. ..#.. ..#.. ..#.. ..#..
U #...# #...# #...# #...# #...# #...# .###.
V #...# #...# #...# #...# #...# .#.#. ..#..
W #...# #...# #...# #.#.# #.#.# ##.## #...#
X #...# #...# .#.#. ..#.. .#.#. #...# #...#
Y #...# #...# .#.#. ..#.. ..#.. ..#.. ..#..
Z ##### ....# ...#. ..#.. .#... #.... #####
0 .###. #...# #..## #.#.# ##..# #...# .###.
1 ..#.. .##.. ..#.. ..#.. ..#.. ..#.. .###.
2 .###. #...# ....# ...#. ..#.. .#... #####
3 ##### ...#. ..##. ....# ....# #...# .###.
4 ...#. ..##. .#.#. #..#. ##### ...#. ...#.
5 ##### #.... ####. ....# ....# #...# .###.
6 ..##. .#... #.... ####. #...# #...# .###.
7 ##### ....# ...#. ..#.. .#... .#... .#...
8 .###. #...# #...# .###. #...# #...# .###.
9 .###. #...# #...# .#### ....# ...#. .##..
. ..... ..... ..... ..... ..... .##.. .##..
, ..... ..... ..... ..... .##.. .##.. .#...
' .##.. .##.. ..#.. ..... ..... ..... .....
- ..... ..... ..... ##### ..... ..... .....
: ..... .##.. .##.. ..... .##.. .##.. .....
/ ....# ....# ...#. ..#.. .#... #.... #....
+ ..... ..#.. ..#.. ##### ..#.. ..#.. .....
! ..#.. ..#.. ..#.. ..#.. ..#.. ..... ..#..
? .###. #...# ....# ...#. ..#.. ..... ..#..
_ ..... ..... ..... ..... ..... ..... #####
"""

G = {}
for line in F.strip().split("\n"):
    parts = line.split(" ")
    ch, rows = parts[0], parts[1:]
    assert len(rows) == 7, f"glyph {ch!r} has {len(rows)} rows"
    assert all(len(r) == 5 for r in rows), f"glyph {ch!r} has a bad row: {rows}"
    G[ch] = rows
G[" "] = ["....."] * 7

CW, CH, ADV = 5, 7, 6


def runs(ch):
    for y, row in enumerate(G.get(ch, G["?"])):
        x = 0
        while x < CW:
            if row[x] == "#":
                w = 1
                while x + w < CW and row[x + w] == "#":
                    w += 1
                yield x, y, w
                x += w
            else:
                x += 1


def width(s, scale):
    return (len(s) * ADV - 1) * scale


def _merge(cells):
    """Merge equal-width runs stacked in consecutive rows into taller rects."""
    cells = sorted(cells)                       # (x, y, w)
    out, used = [], set()
    for i, (cx, cy, cw) in enumerate(cells):
        if i in used:
            continue
        h = 1
        while (cx, cy + h, cw) in [(a, b, c) for a, b, c in cells]:
            j = cells.index((cx, cy + h, cw))
            if j in used:
                break
            used.add(j); h += 1
        out.append((cx, cy, cw, h))
    return out


def rects(s, x, y, scale, anchor="start"):
    """Pixel rects for a string; (x, y) is the top-left of the text box."""
    if anchor == "middle":
        x -= width(s, scale) // 2
    elif anchor == "end":
        x -= width(s, scale)
    out = []
    for i, ch in enumerate(s.upper()):
        ox = x + i * ADV * scale
        cells = [(rx, ry, rw) for rx, ry, rw in runs(ch)]
        for rx, ry, rw, rh in _merge(cells):
            out.append((ox + rx * scale, y + ry * scale, rw * scale, rh * scale))
    return out
