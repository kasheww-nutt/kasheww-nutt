"""The README's panels as a clean dark UI (not ASCII): rounded cards, real charts, pills and chips,
in the knight's palette. The knight banner and the contribution ridge stay ASCII.

    python ui_panels.py static            # experiment cards, method, projects, stack, contact buttons
    python ui_panels.py log commits.json  # activity panel, from the daily workflow's GraphQL answer

Every number below comes from the linked repo's README. Change them there first."""
import datetime as dt
import json
import pathlib
import sys
import textwrap

OUT = pathlib.Path(__file__).resolve().parent.parent / "assets"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Inter','Helvetica Neue',Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,monospace"
BG, CARD, CARD2, LINE, TRACK = "#0c0d12", "#131620", "#0e1017", "#252a36", "#1d222d"
WHITE, TEXT, DIM, FAINT = "#f4f6fb", "#c9ceda", "#8e95a4", "#5d6474"
GOLD, GREEN, AMBER, RED, LINK = "#d9a441", "#3ddc97", "#ffb547", "#ff4d5e", "#7aa7ff"

CSS = f"""text{{font-family:{SANS}}}.m{{font-family:{MONO}}}
.up{{opacity:0;animation:up .6s cubic-bezier(.2,.8,.2,1) forwards}}
@keyframes up{{from{{opacity:0;transform:translateY(8px)}}to{{opacity:1;transform:none}}}}
.bar{{transform-box:fill-box;transform-origin:left center;transform:scaleX(0);animation:grow 1.4s cubic-bezier(.2,.8,.2,1) forwards}}
@keyframes grow{{to{{transform:scaleX(1)}}}}
.live{{animation:live 1.8s ease-in-out infinite}}@keyframes live{{50%{{opacity:.25}}}}
.sheen{{animation:sheen 7s ease-in-out infinite}}@keyframes sheen{{0%,60%{{transform:translateX(-700px)}}100%{{transform:translateX(1300px)}}}}
@media (prefers-reduced-motion:reduce){{*{{animation-duration:0s!important;animation-delay:0s!important}}}}"""


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def width(s, size, bold=False):
    """rough rendered width of sans text"""
    return len(s) * size * (.55 if bold else .5)


def shell(w, h, body, label, glow=GOLD):
    """rounded card with a soft top highlight and a slow light sweep"""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(label)}">
<title>{esc(label)}</title>
<style>{CSS}</style>
<defs>
<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{CARD}"/><stop offset="1" stop-color="{CARD2}"/></linearGradient>
<linearGradient id="top" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{glow}" stop-opacity="0"/><stop offset=".5" stop-color="{glow}" stop-opacity=".8"/><stop offset="1" stop-color="{glow}" stop-opacity="0"/></linearGradient>
<radialGradient id="halo" cx=".15" cy="0" r=".9"><stop offset="0" stop-color="{glow}" stop-opacity=".10"/><stop offset="1" stop-color="{glow}" stop-opacity="0"/></radialGradient>
<linearGradient id="sw" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".035"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<clipPath id="cl"><rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="18"/></clipPath>
</defs>
<rect width="{w}" height="{h}" fill="{BG}"/>
<g clip-path="url(#cl)">
<rect x="1" y="1" width="{w - 2}" height="{h - 2}" fill="url(#bg)"/>
<rect x="1" y="1" width="{w - 2}" height="{h - 2}" fill="url(#halo)"/>
<rect class="sheen" x="0" y="0" width="260" height="{h}" fill="url(#sw)" transform="skewX(-20)"/>
</g>
<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="18" fill="none" stroke="{LINE}"/>
<rect x="40" y="1" width="{w - 80}" height="1.5" fill="url(#top)"/>
{body}
</svg>"""


def eyebrow(x, y, s, col=DIM):
    return f'<text x="{x}" y="{y}" font-size="12" font-weight="600" letter-spacing="1.6" fill="{col}">{esc(s.upper())}</text>'


def pill(x_right, y, s, col, dot=True):
    w = len(s) * (12 * .7 + .8) + (34 if dot else 22)
    x = x_right - w
    d = f'<circle class="live" cx="{x + 14}" cy="{y + 13}" r="3.5" fill="{col}"/>' if dot else ""
    return (f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="26" rx="13" fill="{col}" fill-opacity=".12" stroke="{col}" stroke-opacity=".45"/>'
            f'{d}<text x="{x + (24 if dot else 11):.1f}" y="{y + 17.5}" font-size="12" font-weight="700" letter-spacing=".8" fill="{col}">{esc(s)}</text>')


def chip(x, y, s, col=TEXT, size=13):
    w = width(s, size) + 22
    return (f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="26" rx="8" fill="#ffffff" fill-opacity=".04" stroke="{LINE}"/>'
            f'<text x="{x + 11:.1f}" y="{y + 17.5}" font-size="{size}" fill="{col}">{esc(s)}</text>'), w


def arrow(x, y, col):
    return f'<path d="M{x} {y + 8}L{x + 8} {y}M{x + 2} {y}H{x + 8}V{y + 6}" stroke="{col}" stroke-width="1.8" fill="none" stroke-linecap="round"/>'


def check(x, y, col=GREEN):
    return (f'<circle cx="{x}" cy="{y}" r="8" fill="{col}" fill-opacity=".14"/>'
            f'<path d="M{x - 3.5} {y}l2.5 2.6 4.8-5" stroke="{col}" stroke-width="1.8" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')


def footer_link(w, h, text, sub, col=LINK, icon=True):
    return (f'<line x1="32" y1="{h - 58}" x2="{w - 32}" y2="{h - 58}" stroke="{LINE}"/>'
            + (arrow(33, h - 38, col) if icon else "")
            + f'<text x="{52 if icon else 32}" y="{h - 26}" font-size="14" font-weight="600" fill="{col}">{esc(text)}</text>'
            + f'<text x="{w - 32}" y="{h - 26}" font-size="12" fill="{FAINT}" text-anchor="end">{esc(sub)}</text>')


def save(name, svg):
    (OUT / name).write_text(svg, encoding="utf-8", newline="\n")
    print(f"wrote {name}: {len(svg) / 1e3:.1f} KB")


# ---------------------------------------------------------------- experiment cards (2 x 2)
CW_, CH_ = 552, 384
EXPERIMENTS = [
    dict(slug="card-aqi", n="01", tag="Air quality forecasting", verdict=("BEAT BASELINE", GREEN),
         q='Can a model beat "tomorrow = today" for Delhi air quality?',
         unit="macro-F1 on the locked 2025 test year", lo=.55, hi=.62, fmt="{:.3f}",
         bars=[("LightGBM + CAMS", .600, GREEN), ("Persistence", .583, DIM), ("LightGBM, no CAMS", .574, FAINT)],
         notes=["34 stations · 12,200 station-days · scored once",
                "It only wins with the physics forecast as a feature"],
         link="delhi-aqi-agentic-forecast"),
    dict(slug="card-agri", n="02", tag="Crop disease", verdict=("BEAT BEST SINGLE", GREEN),
         q="Do three CNNs together beat the best one?",
         unit="accuracy on wheat", lo=.80, hi=.95, fmt="{:.1%}",
         bars=[("3-CNN ensemble", .910, GREEN), ("Best single CNN", .880, DIM)],
         notes=["Helps on hard crops like wheat; easy crops barely move",
                "Pre-audit numbers, being rebuilt crop by crop"],
         link="AgriMinds"),
    dict(slug="card-eda", n="03", tag="Synthetic sensor data", verdict=("NO GAIN", AMBER),
         q="Does diffusion-generated sensor data help stress detection?",
         folds=15,
         notes=["Leave-one-subject-out: the test person never trains",
                "The classifier was already at 0.90 with 5% of the data"],
         link=None),
    dict(slug="card-spec", n="04", tag="LLM inference", verdict=("SLOWER", RED),
         q="Is speculative decoding faster in Hindi and Urdu?",
         unit="speedup vs the target model alone, best K", lo=0, hi=1.1, fmt="{:.2f}×", ref=1.0,
         bars=[("English", .92, RED), ("Hindi", .85, RED), ("Urdu", .71, RED)],
         notes=["Qwen2.5 0.5B drafting for 3B on an RTX 4060 laptop",
                "Urdu accepted the fewest draft tokens"],
         link="speculative-decoding-multilingual"),
]


def card(e):
    w, h = CW_, CH_
    out = [eyebrow(32, 46, f'Experiment {e["n"]} · {e["tag"]}'), pill(w - 28, 27, e["verdict"][0], e["verdict"][1])]
    y = 90
    for line in textwrap.wrap(e["q"], 40):
        out.append(f'<text class="up" x="32" y="{y}" font-size="21" font-weight="700" fill="{WHITE}">{esc(line)}</text>')
        y += 28
    y += 10
    if "bars" in e:
        out.append(f'<text x="32" y="{y}" font-size="12" fill="{FAINT}">{esc(e["unit"])} · axis starts at {e["fmt"].format(e["lo"])}</text>')
        y += 16
        x0, x1 = 186, w - 112
        span = x1 - x0
        n = len(e["bars"])
        if "ref" in e:
            xr = x0 + (e["ref"] - e["lo"]) / (e["hi"] - e["lo"]) * span
        for i, (lab, v, col) in enumerate(e["bars"]):
            fill = (v - e["lo"]) / (e["hi"] - e["lo"]) * span
            out.append(f'<text x="32" y="{y + 15}" font-size="14" fill="{TEXT}">{esc(lab)}</text>'
                       f'<rect x="{x0}" y="{y + 5}" width="{span}" height="12" rx="6" fill="{TRACK}"/>'
                       f'<rect class="bar" style="animation-delay:{.25 + i * .2:.2f}s" x="{x0}" y="{y + 5}" width="{fill:.1f}" height="12" rx="6" fill="{col}"/>'
                       f'<text class="m" x="{w - 32}" y="{y + 16}" font-size="15" font-weight="700" fill="{col if col != FAINT else DIM}" text-anchor="end">{e["fmt"].format(v)}</text>')
            y += 30
        if "ref" in e:
            out.append(f'<line x1="{xr:.1f}" y1="{y - 30 * n - 2}" x2="{xr:.1f}" y2="{y - 6}" stroke="{WHITE}" stroke-opacity=".7" stroke-dasharray="3 3"/>'
                       f'<text x="{xr:.1f}" y="{y + 9}" font-size="11" fill="{TEXT}" text-anchor="middle">1.00× = no gain</text>')
            y += 14
    else:
        out.append(f'<text x="32" y="{y}" font-size="12" fill="{FAINT}">one circle per held-out person · filled = significant gain</text>')
        y += 26
        for i in range(e["folds"]):
            out.append(f'<circle class="up" style="animation-delay:{.2 + i * .06:.2f}s" cx="{42 + i * 24}" cy="{y}" r="8" fill="none" stroke="{AMBER}" stroke-width="2"/>')
        y += 30
        out.append(f'<text x="32" y="{y}" font-size="15" font-weight="700" fill="{AMBER}">0 of {e["folds"]} significant</text>')
        y += 12
    y += 18
    for note in e["notes"]:
        out.append(f'<circle cx="36" cy="{y - 4.5}" r="2" fill="{FAINT}"/><text x="46" y="{y}" font-size="13.5" fill="{DIM}">{esc(note)}</text>')
        y += 22
    if e["link"]:
        out.append(footer_link(w, h, e["link"], "view the repo"))
    else:
        out.append(footer_link(w, h, "Repository private for now", "", FAINT, icon=False))
    return shell(w, h, "\n".join(out), f'{e["q"]} Verdict: {e["verdict"][0].lower()}.', e["verdict"][1])


# ---------------------------------------------------------------- method
RULES = [
    ("Beat the dumb baseline first", 'Persistence ("tomorrow = today") is in every AQI comparison.'),
    ("Lock the test set", "The 2025 test year is hashed and scored exactly once."),
    ("Split by time, or by person", "Train 2018-22, test 2025. Leave-one-subject-out on WESAD."),
    ("Make leakage impossible", "45 features carry their day offset; a guard halts the run."),
    ("Publish the losses", "0.92× and 'no gain' sit on this page next to the wins."),
    ("Make it rerunnable", "Pinned versions, fixed seeds, an audit that needs no GPU."),
]


def method():
    w, h = 1118, 420
    out = [eyebrow(40, 50, "Method"),
           f'<text x="40" y="88" font-size="28" font-weight="700" fill="{WHITE}">How I try not to fool myself</text>']
    cols, tw_, th_ = 3, (w - 80 - 2 * 16) / 3, 104
    for i, (rule, ex) in enumerate(RULES):
        c, r = i % cols, i // cols
        x, y = 40 + c * (tw_ + 16), 116 + r * (th_ + 16)
        out.append(f'<g class="up" style="animation-delay:{.15 + i * .12:.2f}s">'
                   f'<rect x="{x:.1f}" y="{y}" width="{tw_:.1f}" height="{th_}" rx="12" fill="#ffffff" fill-opacity=".025" stroke="{LINE}"/>'
                   f'<text class="m" x="{x + 18:.1f}" y="{y + 32}" font-size="13" font-weight="700" fill="{GOLD}">{i + 1:02d}</text>'
                   f'<text x="{x + 48:.1f}" y="{y + 32}" font-size="16" font-weight="700" fill="{WHITE}">{esc(rule)}</text>')
        for k, line in enumerate(textwrap.wrap(ex, 44)):
            out.append(f'<text x="{x + 18:.1f}" y="{y + 60 + k * 20}" font-size="13.5" fill="{DIM}">{esc(line)}</text>')
        out.append("</g>")
    out.append(f'<text x="40" y="{h - 34}" font-size="15" font-style="italic" fill="{TEXT}">“You must not fool yourself, and you are the easiest person to fool.”'
               f'<tspan font-style="normal" font-size="13" fill="{GOLD}">   Richard Feynman</tspan></text>')
    return shell(w, h, "\n".join(out), "How I try not to fool myself: baseline first, a locked test set, splits by time or person, "
                 "no leakage, publish the losses, make it rerunnable.")


# ---------------------------------------------------------------- projects (1 x 2)
PROJECTS = [
    dict(slug="proj-tracker", tag="Full-stack app", name="Fitness tracker",
         what="A fitness and nutrition tracker I actually use every day.",
         checks=["Typecheck and build on every push", "14 test files", "Smoke test: auth, MCP logging, backup and restore"],
         chips=["Next.js", "SQLite", "OAuth (PKCE)", "Docker"],
         link=("lean-muscle-tracker", "view the repo"), col=GREEN),
    dict(slug="proj-civic", tag="Hackathon · one week", name="CivicPulse AI",
         what="Photograph a pothole and the app files the report.",
         flow=["Photo", "Vision model", "Category + severity", "Report filed"],
         chips=["AI vision", "Live map", "Geofenced alerts"],
         link=("Open the live demo", "wakes in ~30 s"), col=LINK),
]


def project(p):
    w, h = CW_, 316
    out = [eyebrow(32, 46, p["tag"]),
           f'<text x="32" y="84" font-size="22" font-weight="700" fill="{WHITE}">{esc(p["name"])}</text>',
           f'<text x="32" y="112" font-size="14.5" fill="{TEXT}">{esc(p["what"])}</text>']
    y = 146
    if "checks" in p:
        for i, c in enumerate(p["checks"]):
            out.append(f'<g class="up" style="animation-delay:{.2 + i * .15:.2f}s">{check(40, y - 5)}'
                       f'<text x="58" y="{y}" font-size="13.5" fill="{TEXT}">{esc(c)}</text></g>')
            y += 26
    else:
        x = 32
        for i, s in enumerate(p["flow"]):
            bw = width(s, 12.5, True) + 18
            out.append(f'<g class="up" style="animation-delay:{.2 + i * .18:.2f}s"><rect x="{x:.1f}" y="{y - 20}" width="{bw:.1f}" height="30" rx="8" '
                       f'fill="{LINK}" fill-opacity="{.08 + i * .05:.2f}" stroke="{LINK}" stroke-opacity=".35"/>'
                       f'<text x="{x + 9:.1f}" y="{y}" font-size="12.5" font-weight="600" fill="{WHITE}">{esc(s)}</text></g>')
            x += bw
            if i < len(p["flow"]) - 1:
                out.append(f'<path d="M{x + 4:.1f} {y - 5}h10m-4 -4l4 4-4 4" stroke="{GOLD}" stroke-width="1.6" fill="none"/>')
                x += 18
        y += 34
    x = 32
    for s in p["chips"]:
        c, cw = chip(x, y - 4, s, DIM, 12.5)
        out.append(c)
        x += cw + 8
    out.append(footer_link(w, h, p["link"][0], p["link"][1], p["col"]))
    return shell(w, h, "\n".join(out), f'{p["name"]}: {p["what"]}', p["col"])


# ---------------------------------------------------------------- stack
STACK = [
    ("Machine learning", GREEN, [("PyTorch", "diffusion study"), ("LightGBM", "air quality"), ("scikit-learn", "air quality"),
                                 ("Transformers", "speculative decoding"), ("LangGraph", "air quality"), ("SHAP", "air quality")]),
    ("Web", LINK, [("TypeScript", "fitness tracker"), ("React", "air quality console"), ("Next.js", "fitness tracker"), ("FastAPI", "air quality API")]),
    ("Infrastructure", AMBER, [("Docker", "fitness tracker"), ("SQLite", "fitness tracker"), ("GitHub Actions", "this page"), ("AWS EC2", "fitness tracker")]),
    ("Languages", GOLD, [("Python", "most of it"), ("TypeScript", "web"), ("Java", "IntelliBill"), ("SQL", "")]),
]


def stack():
    w, h = 1118, 436
    out = [eyebrow(40, 50, "Stack"),
           f'<text x="40" y="88" font-size="28" font-weight="700" fill="{WHITE}">Tools, and where I used them</text>']
    colw = (w - 80) / len(STACK)
    for c, (head, col, items) in enumerate(STACK):
        x = 40 + c * colw
        out.append(f'<rect x="{x:.0f}" y="118" width="18" height="3" rx="1.5" fill="{col}"/>'
                   f'<text x="{x:.0f}" y="144" font-size="13" font-weight="700" letter-spacing="1" fill="{col}">{esc(head.upper())}</text>')
        for i, (name, where) in enumerate(items):
            y = 178 + i * 40
            out.append(f'<g class="up" style="animation-delay:{.15 + c * .12 + i * .06:.2f}s">'
                       f'<text x="{x:.0f}" y="{y}" font-size="15.5" font-weight="600" fill="{WHITE}">{esc(name)}</text>'
                       + (f'<text x="{x:.0f}" y="{y + 17}" font-size="12" fill="{FAINT}">{esc(where)}</text>' if where else "") + "</g>")
    return shell(w, h, "\n".join(out), "Stack: PyTorch, LightGBM, scikit-learn, Transformers, LangGraph, TypeScript, React, Next.js, FastAPI, "
                 "Docker, SQLite, GitHub Actions, AWS EC2, Python, Java, SQL.")


# ---------------------------------------------------------------- contact buttons
def button(label, aria, col=GOLD):
    w, h = int(width(label, 16, True) + 76), 54
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(aria)}">
<style>text{{font-family:{SANS}}}</style>
<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="27" fill="{col}" fill-opacity=".1" stroke="{col}" stroke-opacity=".6"/>
<text x="28" y="{h / 2 + 6:.1f}" font-size="16" font-weight="700" fill="{col}">{esc(label)}</text>
{arrow(w - 38, h / 2 - 4, col)}
</svg>"""


# ---------------------------------------------------------------- activity (daily)
def ago(iso, now):
    d = (now - dt.datetime.fromisoformat(iso.replace("Z", "+00:00"))).total_seconds()
    for s, u in ((86400 * 30, "mo"), (86400 * 7, "w"), (86400, "d"), (3600, "h"), (60, "m")):
        if d >= s:
            return f"{int(d // s)}{u} ago"
    return "just now"


def activity(data, user, now=None, rows=6):
    now = now or dt.datetime.now(dt.timezone.utc)
    commits = []
    for r in data["data"]["user"]["repositories"]["nodes"]:
        if r["name"].lower() == user.lower() or not r.get("defaultBranchRef"):
            continue
        for c in r["defaultBranchRef"]["target"]["history"]["nodes"]:
            commits.append((c["committedDate"], r["name"], c["abbreviatedOid"], c["messageHeadline"]))
    commits.sort(reverse=True)
    commits = commits[:rows]
    w = 1118
    h = 132 + 52 * max(1, len(commits)) + 20
    out = [eyebrow(40, 50, "Activity"),
           f'<text x="40" y="88" font-size="28" font-weight="700" fill="{WHITE}">Lab log</text>',
           pill(w - 40, 64, f"UPDATED {now:%b %d}".upper(), GREEN)]
    y = 136
    if commits:
        out.append(f'<line x1="48" y1="{y}" x2="48" y2="{y + 52 * (len(commits) - 1)}" stroke="{LINE}" stroke-width="2"/>')
    for i, (when, repo, oid, msg) in enumerate(commits):
        msg = msg if len(msg) <= 70 else msg[:69] + "…"
        rw = width(repo, 12, True) + 20
        out.append(f'<g class="up" style="animation-delay:{.15 + i * .12:.2f}s">'
                   f'<circle cx="48" cy="{y}" r="6" fill="{GREEN if i == 0 else CARD}" stroke="{GREEN if i == 0 else FAINT}" stroke-width="2"/>'
                   f'<text x="72" y="{y + 5}" font-size="15" fill="{WHITE}">{esc(msg)}</text>'
                   f'<rect x="{w - 40 - 96 - rw:.1f}" y="{y - 12}" width="{rw:.1f}" height="24" rx="7" fill="{GOLD}" fill-opacity=".1" stroke="{GOLD}" stroke-opacity=".35"/>'
                   f'<text x="{w - 40 - 86 - rw:.1f}" y="{y + 4}" font-size="12" font-weight="600" fill="{GOLD}">{esc(repo)}</text>'
                   f'<text class="m" x="{w - 40}" y="{y + 4}" font-size="12.5" fill="{DIM}" text-anchor="end">{ago(when, now)}</text></g>')
        y += 52
    if not commits:
        out.append(f'<text x="40" y="{y}" font-size="15" fill="{DIM}">A quiet week: nothing pushed to a public repo.</text>')
    return shell(w, h, "\n".join(out), "The latest commits across my public repositories, redrawn daily.", GREEN)


if __name__ == "__main__":
    if sys.argv[1] == "static":
        for e in EXPERIMENTS:
            save(e["slug"] + ".svg", card(e))
        save("method.svg", method())
        for p in PROJECTS:
            save(p["slug"] + ".svg", project(p))
        save("tools.svg", stack())
        save("linkedin.svg", button("LinkedIn", "LinkedIn"))
        save("email.svg", button("Email", "Email"))
    elif sys.argv[1] == "log":
        user = sys.argv[3] if len(sys.argv) > 3 else "kasheww-nutt"
        save("activity.svg", activity(json.load(open(sys.argv[2], encoding="utf-8")), user))
