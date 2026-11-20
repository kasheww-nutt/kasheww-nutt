"""The contribution year as an ASCII mountain range, in the banner's style: each week a slice
of ridge as high as that week's commits, a dim far range behind for depth, snow glyphs on the
crest, the banner's gold glyph moon hanging over the best week. On load the range builds up
row by row; then the stars twinkle and a low mist drifts along the foot of the mountains.

    python contrib_ridge.py contrib.json contrib.svg"""
import datetime as dt
import json
import math
import random
import sys

import numpy as np

import ascii_sky

MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"
W, H = 1118, 340
BG, FRAME, GOLD, DIM, TEXT, GREEN = "#0c0d12", "#3a3f4c", "#d9a441", "#8e95a4", "#d4d8e0", "#a8dc74"
X0, X1, BASE, TOP = 64, W - 64, 262, 150       # ridge spans X0..X1, foot at BASE, crest at most TOP px high
PX, PY, FS = 5.6, 8.6, 10.5                    # glyph cell and size
RAMP = ".:-=+*#%@"
FRONT = ["#3d4558", "#6f7890", "#a9b2c6", "#dde3ee", "#f7f9fd"]   # foot -> crest, then snow
BACK = ["#2b3346", "#465069"]


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def profile(weeks):
    wk = np.array([sum(d["contributionCount"] for d in w["contributionDays"]) for w in weeks], float)
    top = wk.max() or 1
    n = len(wk)
    xs = np.arange(X0, X1, PX)
    pos = (xs - X0) / (X1 - X0) * (n - 1)
    raw = np.interp(pos, np.arange(n), (wk / top) ** .55)               # gentler scale: small weeks still rise
    k = np.exp(-np.arange(-6, 7) ** 2 / 10.0)
    front = np.maximum(np.convolve(raw, k / k.sum(), "same"), raw * .9)
    jag = .035 * np.sin(xs / 7.3) + .025 * np.sin(xs / 3.1 + 1)        # a rocky edge
    front = np.clip(front + jag * (front > .04), 0, 1)
    kb = np.exp(-np.arange(-30, 31) ** 2 / 260.0)
    far = np.convolve(raw, kb / kb.sum(), "same")
    u = (xs - X0) / (X1 - X0)
    # a distant range that is always there, swelling where the year was busiest
    back = .28 + .5 * far / (far.max() or 1) + .14 * np.sin(u * 17 + 1) * np.sin(u * 5.3) + .06 * np.sin(xs / 9)
    return xs, front * TOP, np.clip(back, .08, 1) * TOP * .62, wk


def rows_svg(xs, hgt, palette, cls, back=False):
    """one <text> per glyph row and shade, stretched to the grid so every font lines up"""
    out = []
    nrows = int(TOP / PY) + 2
    for j in range(nrows):
        y = BASE - j * PY
        lines = {s: [" "] * len(xs) for s in range(len(palette))}
        for i, h in enumerate(hgt):
            if j * PY >= h:
                continue
            t = j * PY / max(h, 1)
            if back:
                s, g = (1 if t > .7 else 0), (":" if t > .7 else ".")
            elif h - j * PY < PY * 1.1 and h > 30:
                s, g = len(palette) - 1, "@" if (i + j) % 3 else "%"       # snow on the crest
            else:
                kk = .2 + .8 * t ** 1.3
                s = min(len(palette) - 2, int(kk * (len(palette) - 1)))
                g = RAMP[min(len(RAMP) - 1, int(kk * len(RAMP)))]
            lines[s][i] = g
        for s, chars in lines.items():
            body = "".join(chars)
            if not body.strip():
                continue
            lead = len(body) - len(body.lstrip())
            core = body.strip()
            out.append(f'<text class="{cls}" x="{X0 + lead * PX:.1f}" y="{y:.1f}" fill="{palette[s]}" '
                       f'textLength="{len(core) * PX:.1f}" lengthAdjust="spacingAndGlyphs" '
                       f'style="animation-delay:{.15 + j * .07:.2f}s">{esc(core)}</text>')
    return "".join(out)


def clouds(seed=9):
    """small ASCII clouds blowing left to right across the sky, behind the mountains, looping"""
    rng = random.Random(seed)
    # (y, cols, rows, seconds to cross, phase, opacity)
    lanes = [(78, 24, 4, 70, .05, .7), (112, 18, 3, 92, .45, .55), (96, 28, 5, 80, .72, .65),
             (140, 16, 3, 110, .25, .45), (70, 14, 3, 120, .9, .5)]
    out = []
    for y, cols, rows, dur, phase, op in lanes:
        art = ascii_sky.cloud_art(cols, rows, rng)
        width = cols * ascii_sky.PITCH
        half = max(1, rows // 2)
        lit = ascii_sky._rows(art[:half], 0, 0, "#c3cbe0")                       # moonlit tops
        shade = ascii_sky._rows(art[half:], 0, half * ascii_sky.ROW, "#7d86a3")
        out.append(f'<g transform="translate(0 {y})"><g class="cl" style="--w:{W + width + 40:.0f}px;'
                   f'animation-duration:{dur}s;animation-delay:-{phase * dur:.1f}s" opacity="{op}">'
                   f'<g transform="translate(-{width + 20:.0f} 0)">{lit}{shade}</g></g></g>')
    return "".join(out)


def build(data, user="kasheww-nutt"):
    cal = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    weeks = cal["weeks"]
    days = [d for w in weeks for d in w["contributionDays"]]
    xs, front, back, wk = profile(weeks)
    best_day = max(days, key=lambda d: d["contributionCount"])
    active = sum(1 for d in days if d["contributionCount"])
    run = longest = 0
    for d in days:
        run = run + 1 if d["contributionCount"] else 0
        longest = max(longest, run)
    n = len(weeks)
    wx = lambda c: X0 + c / (n - 1) * (X1 - X0)
    peak = int(np.argmax(wk))
    px = wx(peak)
    ph = float(np.interp(px, xs, front))

    # stars, kept clear of the text and the moon
    rng = random.Random(7)
    stars = []
    while len(stars) < 46:
        x, y = rng.uniform(30, W - 30), rng.uniform(70, BASE - 40)
        if y > BASE - float(np.interp(x, xs, back)) - 14 or abs(x - px) < 40 and y < BASE - ph:
            continue
        ch = rng.choice("..··*")
        stars.append(f'<text x="{x:.0f}" y="{y:.0f}" fill="#9aa3bb" font-size="{rng.choice((8, 9, 10))}" '
                     f'class="tw" style="animation-delay:-{rng.uniform(0, 5):.1f}s;animation-duration:{rng.uniform(2.5, 5):.1f}s">{ch}</text>')

    months, seen = [], None
    for c, w in enumerate(weeks):
        m = dt.date.fromisoformat(w["contributionDays"][0]["date"]).strftime("%b").lower()
        if m != seen and c < n - 2:
            months.append(f'<text x="{wx(c):.1f}" y="{BASE + 20}" fill="{DIM}">{m}</text>')
            seen = m
    # the other notable peaks get a small count
    marks = []
    order = sorted(range(n), key=lambda c: -wk[c])
    taken = [peak]
    for c in order[1:]:
        if len(marks) >= 3 or wk[c] < 10:
            break
        if all(abs(c - t) > 4 for t in taken):
            x = wx(c)
            y = BASE - float(np.interp(x, xs, front)) - 10
            marks.append(f'<text x="{x:.1f}" y="{y:.1f}" fill="{DIM}" font-size="11" text-anchor="middle" class="lbl">{int(wk[c])}</text>')
            taken.append(c)
    # hover: each week as a strip with its own tooltip
    tips = "".join(f'<rect x="{wx(c) - (X1 - X0) / (n - 1) / 2:.1f}" y="60" width="{(X1 - X0) / (n - 1):.1f}" '
                   f'height="{BASE - 60}" fill="transparent"><title>week of {w["contributionDays"][0]["date"]}: '
                   f'{int(wk[c])} contributions</title></rect>' for c, w in enumerate(weeks))
    stats = [("total", str(cal["totalContributions"])), ("active days", str(active)),
             ("longest streak", f"{longest}d"),
             ("best day", f"{dt.date.fromisoformat(best_day['date']).strftime('%b %d').lower()} · {best_day['contributionCount']}"),
             ("best week", str(int(wk[peak])))]
    sx, st = 48, []
    for k, v in stats:
        st.append(f'<text x="{sx}" y="{H - 34}"><tspan fill="{DIM}">&gt; {k} </tspan><tspan fill="{GREEN}" font-weight="700">{esc(v)}</tspan></text>')
        sx += 8.5 * (len(k) + len(v) + 4) + 20
    title = "CONTRIBUTIONS"
    tw = 9.6 * (len(title) + 4)
    moon = ascii_sky.moon(round(px), round(BASE - ph - 46), 17)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{cal['totalContributions']} contributions in the last year, drawn as a mountain range">
<style>
text{{font-family:{MONO};white-space:pre}}
.r{{font-size:{FS}px;font-weight:700;opacity:0;animation:rise .5s ease-out forwards}}
@keyframes rise{{from{{opacity:0;transform:translateY(5px)}}to{{opacity:1;transform:none}}}}
.mn,.lbl{{opacity:0;animation:fade 1.2s 1.6s ease-out forwards}}
@keyframes fade{{to{{opacity:1}}}}
.mn > g{{animation:pulse 5s 2.8s ease-in-out infinite alternate}}
@keyframes pulse{{from{{opacity:.85}}to{{opacity:1}}}}
.tw{{animation:tw 4s ease-in-out infinite}}
@keyframes tw{{0%,100%{{opacity:.25}}50%{{opacity:1}}}}
.mist{{animation:mist 26s linear infinite}}
@keyframes mist{{from{{transform:translateX(0)}}to{{transform:translateX(-{W}px)}}}}
.cl{{animation-name:cl;animation-timing-function:linear;animation-iteration-count:infinite}}
@keyframes cl{{from{{transform:translateX(0)}}to{{transform:translateX(var(--w))}}}}
.cur{{animation:blink 1.1s steps(1) infinite}}
@keyframes blink{{50%{{opacity:0}}}}
</style>
<defs>{ascii_sky.DEFS}
<clipPath id="inner"><rect x="20" y="24" width="{W - 40}" height="{H - 40}"/></clipPath>
<radialGradient id="mistR"><stop offset="0" stop-color="#b9c4dc" stop-opacity=".16"/><stop offset="1" stop-color="#b9c4dc" stop-opacity="0"/></radialGradient>
<linearGradient id="mistG" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#b9c4dc" stop-opacity="0"/><stop offset=".25" stop-color="#b9c4dc" stop-opacity=".16"/><stop offset=".5" stop-color="#b9c4dc" stop-opacity=".05"/><stop offset=".75" stop-color="#b9c4dc" stop-opacity=".16"/><stop offset="1" stop-color="#b9c4dc" stop-opacity="0"/></linearGradient>
<linearGradient id="skyR" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#121a3a" stop-opacity="0"/><stop offset="1" stop-color="#1b2a5c" stop-opacity=".35"/></linearGradient>
</defs>
<rect width="{W}" height="{H}" fill="{BG}"/>
<rect x="20" y="40" width="{W - 40}" height="{BASE - 40}" fill="url(#skyR)"/>
<path d="M18 {H - 14}V22H32 M{32 + tw + 18} 22H{W - 18}V{H - 14}H18" fill="none" stroke="{FRAME}" stroke-dasharray="6 5"/>
<text x="40" y="27" font-size="17" font-weight="700" fill="{GOLD}">[ {title} ]</text>
<text x="40" y="54" font-size="13" fill="{DIM}">contrib.py --render ridge --user {user} --since {days[0]['date']}<tspan class="cur" fill="{TEXT}">_</tspan></text>
<g>{"".join(stars)}</g>
<g class="mn">{moon}<text x="{px + 26:.0f}" y="{BASE - ph - 40:.0f}" font-size="12" fill="{GOLD}">best week · {int(wk[peak])}</text></g>
<g clip-path="url(#inner)">{clouds()}</g>
<g>{rows_svg(xs, back, BACK, "r", back=True)}</g>
<g>{rows_svg(xs, front, FRONT, "r")}</g>
<g>{"".join(marks)}</g>
<g clip-path="url(#inner)"><g class="mist">{"".join(f'<ellipse cx="{cx}" cy="{BASE - 8 + dy}" rx="{rx}" ry="{ry}" fill="url(#mistR)"/>' for cx, dy, rx, ry in ((150, 0, 200, 16), (520, -4, 260, 20), (900, 2, 220, 15), (1268, 0, 200, 16), (1638, -4, 260, 20), (2018, 2, 220, 15)))}</g></g>
<text x="{X0}" y="{BASE + 6}" font-size="9" fill="#2a3040" textLength="{X1 - X0:.0f}" lengthAdjust="spacingAndGlyphs">{":" * int((X1 - X0) / PX)}</text>
<g font-size="12">{"".join(months)}</g>
<g font-size="14">{"".join(st)}</g>
<text x="{W - 40}" y="{H - 18}" font-size="11" fill="#5d6474" text-anchor="end">updated {days[-1]['date']}</text>
<g>{tips}</g>
</svg>"""


if __name__ == "__main__":
    # python contrib_ridge.py contrib.json out.svg [github-user]
    svg = build(json.load(open(sys.argv[1], encoding="utf-8")), *(sys.argv[3:4]))
    open(sys.argv[2], "w", encoding="utf-8").write(svg)
    print(f"wrote {sys.argv[2]}: {len(svg) / 1e3:.0f} KB")
