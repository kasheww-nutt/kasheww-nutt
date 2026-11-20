"""ASCII clouds and an ASCII crescent moon, drawn on the reel's own glyph grid so they match the knight."""
import math
import random

PITCH, ROW = 720 / 154, 8.0          # the reel's glyph cell
FONT = 8.4
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"
RAMP = " .,:-=+*%#"                  # thin to dense; no characters that need escaping


def _rows(art, x, y, fill, extra=""):
    """one <text> per row, stretched to exactly the grid width so every font lines up"""
    out = []
    for i, line in enumerate(art):
        if not line.strip():
            continue
        lead = len(line) - len(line.lstrip())
        body = line.strip()
        out.append(f'<text x="{x + lead * PITCH:.1f}" y="{y + i * ROW:.1f}" font-size="{FONT}" fill="{fill}" '
                   f'textLength="{len(body) * PITCH:.1f}" lengthAdjust="spacingAndGlyphs"{extra}>{body}</text>')
    return "".join(out)


def cloud_art(cols, rows, rng):
    """a puffy cloud: a few overlapping blobs, dense in the middle, wispy at the edges"""
    blobs = [(rng.uniform(.2, .8) * cols, rng.uniform(.35, .7) * rows,
              rng.uniform(.18, .32) * cols, rng.uniform(.38, .6) * rows) for _ in range(4)]
    blobs.append((cols / 2, rows * .62, cols * .46, rows * .42))      # flat-ish base
    art = []
    for r in range(rows):
        line = ""
        for c in range(cols):
            d = max(1 - ((c - bx) / bw) ** 2 - ((r - by) / bh) ** 2 for bx, by, bw, bh in blobs)
            if d <= 0 or (d < .25 and rng.random() < .45):
                line += " "
                continue
            k = min(len(RAMP) - 1, 1 + int(d * (len(RAMP) - 2) * 1.15))
            line += RAMP[k]
        art.append(line.rstrip())
    return art


def clouds(W, seed=5):
    """small ASCII clouds blowing left to right with the wind, looping across the sky"""
    rng = random.Random(seed)
    lanes = [(70, 26, 5, 74, 0.0), (128, 20, 4, 96, .35), (186, 30, 6, 82, .62), (98, 16, 4, 110, .85),
             (238, 22, 4, 104, .18), (52, 18, 4, 120, .5), (160, 14, 3, 132, .75)]
    out = []
    for y, cols, rows, dur, phase in lanes:
        art = cloud_art(cols, rows, rng)
        width = cols * PITCH
        lit = _rows(art[:max(1, rows // 2)], 0, 0, "#c3cbe0")                    # moonlit top
        shade = _rows(art[max(1, rows // 2):], 0, max(1, rows // 2) * ROW, "#7d86a3")
        out.append(f'<g transform="translate(0 {y})"><g class="cl" style="--w:{W + width + 40:.0f}px;'
                   f'animation-duration:{dur}s;animation-delay:-{phase * dur:.1f}s" opacity="{rng.uniform(.55, .8):.2f}">'
                   f'<g transform="translate(-{width + 20:.0f} 0)">{lit}{shade}</g></g></g>')
    return "".join(out)


def moon(cx, cy, r=34):
    """a fine golden crescent like the reference: lit on the right, horns tapering to points,
    the lower horn reaching further left; small dense glyphs in three shades of gold"""
    pitch, row, size = 3.9, 5.0, 6.4                      # finer than the clouds, so it reads as a smooth shape
    cols, rows = int(2.3 * r / pitch), int(2.3 * r / row)
    ox, oy, ir = -.5 * r, -.07 * r, .9 * r               # the shadow disc, nudged up-left so the lower horn is longer
    levels = [[], [], []]
    rng = random.Random(9)
    n = 4
    for j in range(rows):
        lines = [[" "] * cols for _ in range(3)]
        for i in range(cols):
            x0 = (i - cols / 2) * pitch
            y0 = (j - rows / 2) * row
            hit = 0
            for u in range(n):
                for v in range(n):
                    x, y = x0 + (u + .5) * pitch / n, y0 + (v + .5) * row / n
                    hit += (x * x + y * y <= r * r) and ((x - ox) ** 2 + (y - oy) ** 2 > ir * ir)
            cover = hit / (n * n)
            if cover < .3:
                continue
            xc, yc = x0 + pitch / 2, y0 + row / 2
            thick = max(0.0, math.hypot(xc - ox, yc - oy) - ir) / (r - ir + math.hypot(ox, oy))   # 0 at the inner edge
            k = cover * (.55 + .45 * min(1, thick * 3)) * rng.uniform(.8, 1.08)              # a little sparkle
            ch = "@" if k > .78 else "%" if k > .6 else "#" if k > .45 else "*" if k > .36 else ":"
            lvl = 2 if k > .8 else 1 if k > .55 else 0
            lines[lvl][i] = ch
        for lvl in range(3):
            levels[lvl].append("".join(lines[lvl]))
    x0 = cx - cols * pitch / 2
    y0 = cy - rows * row / 2 + row * .8
    shades = ["#8a6428", "#d2a24e", "#f6d98f"]
    out = []
    for lvl in range(3):
        for j, line in enumerate(levels[lvl]):
            if not line.strip():
                continue
            out.append(f'<text x="{x0:.1f}" y="{y0 + j * row:.1f}" font-size="{size}" fill="{shades[lvl]}" '
                       f'textLength="{cols * pitch:.1f}" lengthAdjust="spacingAndGlyphs">{line}</text>')
    return (f'<circle cx="{cx}" cy="{cy}" r="{r * 2.4:.0f}" fill="url(#moonHalo)"/>'
            f'<g filter="url(#moonGlow)">{"".join(out)}</g>')


CSS = """
.sky text{font-family:@@MONO@@;white-space:pre}
.cl{animation-name:cl;animation-timing-function:linear;animation-iteration-count:infinite}
@keyframes cl{from{transform:translateX(0)}to{transform:translateX(var(--w))}}
.moonp{animation:moonp 5s ease-in-out infinite alternate}
@keyframes moonp{from{opacity:.85}to{opacity:1}}
""".replace("@@MONO@@", MONO)

DEFS = ('<radialGradient id="moonHalo"><stop offset="0" stop-color="#f6e2a0" stop-opacity=".22"/>'
        '<stop offset=".4" stop-color="#e8c878" stop-opacity=".08"/><stop offset="1" stop-color="#e8c878" stop-opacity="0"/></radialGradient>'
        '<filter id="moonGlow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="1.2" result="b"/>'
        '<feColorMatrix in="b" type="matrix" values="1.2 0 0 0 .05  0 1.05 0 0 .02  0 0 .7 0 0  0 0 0 1.6 0" result="g"/>'
        '<feMerge><feMergeNode in="g"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
