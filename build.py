#!/usr/bin/env python3
"""
Regenerates dark_mode.svg and light_mode.svg for the GabPey/GabPey profile README.

The card is a neofetch-style terminal panel: ASCII portrait on the left, dotted-leader
fields on the right. Structure follows Andrew6rant/Andrew6rant, minus the GitHub Action —
everything here is static, so edit FIELDS below and re-run:  python3 build.py

Facts come from the vault source notes; see "GitHub Profile README — EN.md".
"""
import html

ART_FILE = "portrait.txt"
FONT_SIZE = 16
CHAR_W    = FONT_SIZE * 0.61    # widest realistic monospace advance (Consolas is 0.55;
                                # macOS/Linux fall back to Menlo/DejaVu at ~0.60, so size for those)
LINE_H    = 20
PAD       = 15
GAP       = 22
VALUE_COL = 17                  # column where values start, in characters

USER = "gabriel@marseille"

# (label, value) — label None = blank line; label starting with "-" = section header
FIELDS = [
    ("-rule", None),
    ("OS",           "Mexico → Netherlands → Mexico → France → Spain"),
    ("Host",         "Aix-Marseille Université · Marseille, France"),
    ("Kernel",       "M2 Applied Mathematics & Statistics · CMB track"),
    ("Uptime",       "25 years"),
    ("Shell",        "Python · R · C++ · Java · Dart"),
    ("Packages",     "Pyro · PyTorch · NumPy/SciPy · CUDA · OpenMP"),
    (None, None),
    ("- Research", None),
    ("Inference",    "Bayesian & variational — SVI, ELBO"),
    ("Sequence",     "deep Markov models · HMMs · forward–backward · Viterbi"),
    ("Signals",      "cardiac electrical activity · fiber photometry"),
    ("Latest",       "PhotoDMM · Abante Lab, Barcelona — paper in prep."),
    (None, None),
    ("- Building", None),
    ("ConceptVerse", "a language-learning system, as a 3D concept atlas"),
    ("Stack",        "Flutter · Dart · SQLite · spaCy · LLM"),
    (None, None),
    ("- Languages", None),
    ("Programming",  "Python, R, C++/CUDA, Java, Dart"),
    ("Spoken",       "Spanish (native) · English C1 · French C1 · German A2"),
    (None, None),
    ("- Next", None),
    ("Looking for",  "6-month research internship · Feb–Aug 2027"),
    ("Toward",       "doctoral research in statistics & ML for health"),
    (None, None),
    ("- Contact", None),
    ("Email",        "gpeytralborja@gmail.com"),
    ("GitHub",       "@GabPey"),
    ("LinkedIn",     "gabriel-peytral-borja"),
]

THEMES = {
    "dark_mode.svg":  dict(bg="#161b22", fg="#c9d1d9", key="#ffa657",
                           value="#a5d6ff", dots="#616e7f", art="#8b949e"),
    "light_mode.svg": dict(bg="#f6f8fa", fg="#24292f", key="#953800",
                           value="#0a3069", dots="#c2cfde", art="#57606a"),
}

e = html.escape


def field_lines():
    """Yield (plain_text, svg_markup) per right-column line."""
    rule_len = max(len(USER), 44)
    for label, value in FIELDS:
        if label == "-rule":
            txt = "─" * rule_len
            yield txt, f'<tspan class="cc">{txt}</tspan>'
        elif label is None:
            yield "", ""
        elif label.startswith("- "):
            yield label, f'<tspan class="key">{e(label)}</tspan>'
        else:
            dots = "." * max(1, VALUE_COL - len(label) - 4)
            txt = f". {label}: {dots} {value}"
            yield txt, (f'<tspan class="cc">. </tspan>'
                        f'<tspan class="key">{e(label)}</tspan>'
                        f'<tspan class="cc">: {dots} </tspan>'
                        f'<tspan class="value">{e(value)}</tspan>')


def build(theme_file, c, art):
    rows = list(field_lines())
    art_w = max(len(l) for l in art)
    right_x = PAD + int(art_w * CHAR_W) + GAP
    width = right_x + int((max(len(t) for t, _ in rows) + 1) * CHAR_W) + PAD
    height = max(len(art), len(rows) + 1) * LINE_H + 2 * PAD

    out = [
        "<?xml version='1.0' encoding='UTF-8'?>",
        f'<svg xmlns="http://www.w3.org/2000/svg" font-family="ConsolasFallback,Consolas,monospace" '
        f'width="{width}px" height="{height}px" font-size="{FONT_SIZE}px">',
        "<style>",
        "@font-face {",
        "src: local('Consolas'), local('Consolas Bold');",
        "font-family: 'ConsolasFallback';",
        "font-display: swap;",
        "-webkit-size-adjust: 109%;",
        "size-adjust: 109%;",
        "}",
        f".key {{fill: {c['key']};}}",
        f".value {{fill: {c['value']};}}",
        f".cc {{fill: {c['dots']};}}",
        f".ascii {{fill: {c['art']};}}",
        "text, tspan {white-space: pre;}",
        "</style>",
        f'<rect width="{width}px" height="{height}px" fill="{c["bg"]}" rx="15"/>',
        f'<text x="{PAD}" y="30" class="ascii">',
    ]
    for i, line in enumerate(art):
        out.append(f'<tspan x="{PAD}" y="{30 + i * LINE_H}">{e(line)}</tspan>')
    out.append("</text>")
    out.append(f'<text x="{right_x}" y="30" fill="{c["fg"]}">')
    out.append(f'<tspan x="{right_x}" y="30">{e(USER)}</tspan>')
    for i, (_, markup) in enumerate(rows, start=1):
        y = 30 + i * LINE_H
        out.append(f'<tspan x="{right_x}" y="{y}">{markup}</tspan>')
    out.append("</text>")
    out.append("</svg>")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    art = open(ART_FILE, encoding="utf-8").read().rstrip("\n").split("\n")
    while art and not art[0].strip():
        art.pop(0)
    for name, colours in THEMES.items():
        open(name, "w", encoding="utf-8").write(build(name, colours, art))
        print("wrote", name)
