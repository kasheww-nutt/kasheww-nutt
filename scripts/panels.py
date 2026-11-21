"""The README's terminal panels, drawn in the same style as the eval panel and the ridge: dashed frame,
gold [ TITLE ], a command line with a blinking cursor, monospace everything.

    python panels.py static            # cards, rules, built, stack, contact buttons (hand-written facts)
    python panels.py log commits.json  # lab log, from the daily workflow's GraphQL answer

Every number below comes from the linked repo's README. Change them there first."""
import datetime as dt
import json
import pathlib
import sys
import textwrap

OUT = pathlib.Path(__file__).resolve().parent.parent / "assets"
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"
BG, FRAME, GOLD, DIM, FAINT, TEXT = "#0c0d12", "#3a3f4c", "#d9a441", "#8e95a4", "#5d6474", "#d4d8e0"
WHITE, GREEN, AMBER, RED, LINK = "#f2f4f8", "#3ddc97", "#ffb547", "#ff3b4e", "#7aa7ff"
CW = .6                                   # monospace advance, in ems

CSS = f"""text{{font-family:{MONO};white-space:pre}}
.cur{{animation:blink 1.1s steps(1) infinite}}@keyframes blink{{50%{{opacity:0}}}}
.ln{{opacity:0;animation:in .35s ease-out forwards}}@keyframes in{{from{{opacity:0;transform:translateX(-6px)}}to{{opacity:1;transform:none}}}}
.bar{{transform-box:fill-box;transform-origin:left center;transform:scaleX(0);animation:grow 1.3s cubic-bezier(.2,.8,.2,1) forwards}}
@keyframes grow{{to{{transform:scaleX(1)}}}}
.dot{{opacity:0;animation:pop .25s steps(2) forwards}}@keyframes pop{{to{{opacity:1}}}}
.pulse{{animation:pulse 2.4s ease-in-out infinite}}@keyframes pulse{{50%{{opacity:.7}}}}
@media (prefers-reduced-motion:reduce){{*{{animation-duration:0s!important;animation-delay:0s!important}}}}"""


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def tw(s, size):
    return len(s) * size * CW


def frame(w, h, title, cmd, body, label, extra_css=""):
    t = f"[ {title} ]"
    gap = tw(t, 17) + 18
    cmdline = (f'<text x="40" y="56" font-size="13" fill="{DIM}">{esc(cmd)}<tspan class="cur" fill="{TEXT}">_</tspan></text>'
               if cmd else "")
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(label)}">
<title>{esc(label)}</title>
<style>{CSS}{extra_css}</style>
<rect width="{w}" height="{h}" fill="{BG}"/>
<path d="M18 {h - 14}V22H32 M{32 + gap:.0f} 22H{w - 18}V{h - 14}H18" fill="none" stroke="{FRAME}" stroke-dasharray="6 5"/>
<text x="40" y="27" font-size="17" font-weight="700" fill="{GOLD}">{esc(t)}</text>
{cmdline}
{body}
</svg>"""


def chip(x_right, y, text, col):
    w = tw(text, 12) + 16
    return (f'<g class="pulse"><rect x="{x_right - w:.1f}" y="{y - 13}" width="{w:.1f}" height="19" fill="{col}" fill-opacity=".14" '
            f'stroke="{col}" stroke-opacity=".7"/><text x="{x_right - w / 2:.1f}" y="{y + 1}" font-size="12" font-weight="700" '
            f'fill="{col}" text-anchor="middle">{esc(text)}</text></g>')


def save(name, svg):
    (OUT / name).write_text(svg, encoding="utf-8", newline="\n")
    print(f"wrote {name}: {len(svg) / 1e3:.1f} KB")


# ---------------------------------------------------------------- experiment cards (2 x 2)
CARD_W, CARD_H = 552, 340
EXPERIMENTS = [
    dict(slug="exp-aqi", n="01", name="DELHI AIR QUALITY", verdict=("BEAT BASELINE", GREEN),
         cmd="$ evaluate --vs persistence --test-year 2025",
         q='Can a model beat "tomorrow = today" for Delhi air quality?',
         unit="macro-F1", lo=.55, hi=.62, fmt="{:.3f}",
         bars=[("lightgbm + cams", .600, GREEN), ("persistence", .583, DIM), ("lightgbm, no cams", .574, FAINT)],
         notes=["34 stations · 12,200 station-days · test year scored once",
                "it only wins with the physics forecast as a feature"],
         link="github.com/kasheww-nutt/delhi-aqi-agentic-forecast"),
    dict(slug="exp-agri", n="02", name="CROP DISEASE ENSEMBLE", verdict=("BEAT BEST SINGLE", GREEN),
         cmd="$ evaluate --crop wheat --ensemble 3",
         q="Do three CNNs together beat the best one?",
         unit="accuracy, wheat", lo=.80, hi=.95, fmt="{:.1%}",
         bars=[("3-cnn ensemble", .910, GREEN), ("best single cnn", .880, DIM)],
         notes=["helps on hard crops like wheat",
                "on easy crops it changed almost nothing",
                "pre-audit numbers; being rebuilt crop by crop"],
         link="github.com/kasheww-nutt/AgriMinds"),
    dict(slug="exp-eda", n="03", name="SYNTHETIC SENSOR DATA", verdict=("NO GAIN", AMBER),
         cmd="$ run_all --loso --augment ddpm",
         q="Does diffusion-generated sensor data help stress detection?",
         folds=15,
         notes=["leave-one-subject-out: the test person never trains",
                "classifier already at 0.90 with 5% of the data"],
         link=None),
    dict(slug="exp-spec", n="04", name="SPECULATIVE DECODING", verdict=("SLOWER", RED),
         cmd="$ bench --draft qwen2.5-0.5b --target qwen2.5-3b",
         q="Is speculative decoding faster in Hindi and Urdu?",
         unit="speedup, best K", lo=0, hi=1.1, fmt="{:.2f}x", ref=1.0,
         bars=[("english", .92, RED), ("hindi", .85, RED), ("urdu", .71, RED)],
         notes=["rtx 4060 laptop · the draft model was not cheap enough",
                "urdu accepted the fewest draft tokens"],
         link="github.com/kasheww-nutt/speculative-decoding-multilingual"),
]


def card(e):
    w, h = CARD_W, CARD_H
    out = [chip(w - 36, 30, e["verdict"][0], e["verdict"][1])]
    y = 92
    for line in textwrap.wrap(e["q"], 44):
        out.append(f'<text x="40" y="{y}" font-size="17" font-weight="700" fill="{WHITE}">{esc(line)}</text>')
        y += 23
    y += 14
    if "bars" in e:
        out.append(f'<text x="40" y="{y}" font-size="12" fill="{FAINT}">{esc(e["unit"])} · axis {e["fmt"].format(e["lo"])} to {e["fmt"].format(e["hi"])}</text>')
        y += 24
        x0, x1 = 196, w - 140
        span = x1 - x0
        if "ref" in e:
            xr = x0 + (e["ref"] - e["lo"]) / (e["hi"] - e["lo"]) * span
            out.append(f'<line x1="{xr:.1f}" y1="{y - 14}" x2="{xr:.1f}" y2="{y + 26 * len(e["bars"]) - 10}" stroke="{TEXT}" stroke-dasharray="2 3"/>'
                       f'<text x="{xr + 6:.1f}" y="{y - 24}" font-size="11" fill="{TEXT}">1.00x = no gain</text>')
        for i, (lab, v, col) in enumerate(e["bars"]):
            n = max(1, round((v - e["lo"]) / (e["hi"] - e["lo"]) * span / (13 * CW)))
            out.append(f'<text x="40" y="{y}" font-size="13" fill="{DIM}">{esc(lab)}</text>')
            out.append(f'<text class="bar" style="animation-delay:{.3 + i * .25:.2f}s" x="{x0}" y="{y}" font-size="13" fill="{col}">{"█" * n}</text>')
            out.append(f'<text class="ln" style="animation-delay:{1.2 + i * .25:.2f}s" x="{x1 + 22}" y="{y}" '
                       f'font-size="13" font-weight="700" fill="{col}">{e["fmt"].format(v)}</text>')
            y += 26
    else:
        out.append(f'<text x="40" y="{y}" font-size="12" fill="{FAINT}">one dot per held-out person · filled = significant gain</text>')
        y += 26
        for i in range(e["folds"]):
            out.append(f'<text class="dot" style="animation-delay:{.3 + i * .08:.2f}s" x="{40 + i * 21}" y="{y + 2}" font-size="17" fill="{AMBER}">○</text>')
        out.append(f'<text class="ln" style="animation-delay:1.7s" x="{40 + e["folds"] * 21 + 8}" y="{y + 1}" font-size="13" font-weight="700" fill="{AMBER}">0/{e["folds"]} · n.s.</text>')
        y += 40
    y += 6
    for i, note in enumerate(e["notes"]):
        out.append(f'<text x="40" y="{y}" font-size="13" fill="{DIM}"><tspan fill="{FAINT}"># </tspan>{esc(note)}</text>')
        y += 20
    foot = (f'<text x="40" y="{h - 30}" font-size="13" fill="{LINK}">→ {esc(e["link"])}</text>' if e["link"] else
            f'<text x="40" y="{h - 30}" font-size="13" fill="{FAINT}">→ repo private for now</text>')
    out.append(foot)
    label = f'{e["q"]} {e["verdict"][0].lower()}.'
    return frame(w, h, f'{e["n"]} · {e["name"]}', e["cmd"], "\n".join(out), label)


# ---------------------------------------------------------------- rules
RULES = [
    ("beat the dumb baseline first", 'persistence ("tomorrow = today") is in every AQI comparison'),
    ("lock the test set", "the 2025 test year is hashed and scored exactly once"),
    ("split by time, or by person", "train 2018-22 → test 2025 · leave-one-subject-out on WESAD"),
    ("make leakage impossible", "45 features carry their day offset; a guard halts the run"),
    ("publish the losses", "0.92x and n.s. are on this page, next to the wins"),
    ("make it rerunnable", "pinned versions, fixed seeds, an audit that needs no GPU"),
]


def rules():
    w, h = 1118, 352
    out = []
    y = 100
    for i, (rule, ex) in enumerate(RULES):
        d = .4 + i * .32
        out.append(f'<g class="ln" style="animation-delay:{d:.2f}s"><text x="40" y="{y}" font-size="15">'
                   f'<tspan fill="{FAINT}">{i + 1:02d} </tspan><tspan fill="{GREEN}">[✓] </tspan>'
                   f'<tspan fill="{WHITE}" font-weight="700">{esc(rule)}</tspan></text>'
                   f'<text x="430" y="{y}" font-size="13" fill="{DIM}"><tspan fill="{FAINT}">→ </tspan>{esc(ex)}</text></g>')
        y += 33
    out.append(f'<text class="ln" style="animation-delay:{.4 + len(RULES) * .32 + .3:.2f}s" x="40" y="{y + 18}" font-size="13" fill="{FAINT}">'
               f'# "you must not fool yourself, and you are the easiest person to fool." <tspan fill="{GOLD}">feynman</tspan></text>')
    return frame(w, h, "HOW I TRY NOT TO FOOL MYSELF", "$ cat RULES.md", "\n".join(out),
                 "Six rules I hold my experiments to: baseline first, a locked test set, splits by time or person, "
                 "no leakage, publish the losses, make it rerunnable.")


# ---------------------------------------------------------------- built things (1 x 2)
BUILT = [
    dict(slug="built-tracker", name="FITNESS TRACKER", cmd="$ npm test && npm run build",
         what="A fitness and nutrition tracker I actually use every day.",
         lines=[(GREEN, "✓", "typecheck"), (GREEN, "✓", "14 test files, on every push"),
                (GREEN, "✓", "smoke: auth, MCP logging, backup + restore")],
         stack="next.js · sqlite · oauth (pkce) · docker",
         link="github.com/kasheww-nutt/lean-muscle-tracker"),
    dict(slug="built-civic", name="CIVICPULSE AI", cmd="$ report --photo pothole.jpg",
         what="Photograph a pothole and the app files the report.",
         flow=["photo", "vision model", "category + severity 1-5", "report filed"],
         lines=[(AMBER, "★", "built in one week for a hackathon"), (LINK, "▶", "live demo, wakes in ~30 s")],
         stack="ai vision · live map · geofenced alerts",
         link="github.com/kasheww-nutt/CivicPulseAI"),
]


def built(b):
    w, h = CARD_W, 262
    out = [f'<text x="40" y="92" font-size="15" font-weight="700" fill="{WHITE}">{esc(b["what"])}</text>']
    y = 124
    if "flow" in b:
        x = 40
        for i, step in enumerate(b["flow"]):
            out.append(f'<text class="ln" style="animation-delay:{.3 + i * .3:.1f}s" x="{x:.1f}" y="{y}" font-size="12" fill="{TEXT}">{esc(step)}</text>')
            x += tw(step, 12)
            if i < len(b["flow"]) - 1:
                out.append(f'<text class="ln" style="animation-delay:{.45 + i * .3:.2f}s" x="{x + 4:.1f}" y="{y}" font-size="12" fill="{GOLD}">→</text>')
                x += 22
        y += 28
    for i, (col, mark, txt) in enumerate(b["lines"]):
        out.append(f'<text class="ln" style="animation-delay:{1.2 + i * .25:.2f}s" x="40" y="{y}" font-size="13" fill="{TEXT}">'
                   f'<tspan fill="{col}">{mark} </tspan>{esc(txt)}</text>')
        y += 22
    out.append(f'<text x="40" y="{h - 52}" font-size="12" fill="{FAINT}"># {esc(b["stack"])}</text>')
    out.append(f'<text x="40" y="{h - 30}" font-size="13" fill="{LINK}">→ {esc(b["link"])}</text>')
    return frame(w, h, b["name"], b["cmd"], "\n".join(out), f'{b["name"].title()}: {b["what"]}')


# ---------------------------------------------------------------- stack
STACK = [
    ("ml/", [("pytorch", "diffusion-eda"), ("lightgbm", "delhi-aqi"), ("scikit-learn", "delhi-aqi"),
             ("transformers", "spec-decoding"), ("langgraph", "delhi-aqi"), ("shap", "delhi-aqi")]),
    ("web/", [("typescript", "tracker"), ("react", "delhi-aqi"), ("next.js", "tracker"), ("fastapi", "delhi-aqi")]),
    ("infra/", [("docker", "tracker"), ("sqlite", "tracker"), ("gh actions", "this page"), ("aws ec2", "tracker")]),
    ("langs/", [("python", "most of it"), ("typescript", "web"), ("java", "intellibill"), ("sql", "")]),
]


def stack():
    w, h = 1118, 306
    out = []
    colw = (w - 80) / len(STACK)
    for c, (head, items) in enumerate(STACK):
        x = 40 + c * colw
        out.append(f'<text x="{x:.0f}" y="96" font-size="15" font-weight="700" fill="{GOLD}">{esc(head)}</text>')
        for i, (name, where) in enumerate(items):
            branch = "└── " if i == len(items) - 1 else "├── "
            out.append(f'<text class="ln" style="animation-delay:{.3 + c * .2 + i * .1:.2f}s" x="{x:.0f}" y="{122 + i * 24}" font-size="14" fill="{TEXT}">'
                       f'<tspan fill="{FAINT}">{branch}</tspan>{esc(name)}'
                       + (f'<tspan fill="{FAINT}" font-size="11">  {esc(where)}</tspan>' if where else "") + "</text>")
    out.append(f'<text x="40" y="{h - 30}" font-size="12" fill="{FAINT}"># each tool is listed next to a repo that uses it</text>')
    return frame(w, h, "STACK", "$ tree ~/stack --used-in", "\n".join(out),
                 "Stack: PyTorch, LightGBM, scikit-learn, Transformers, LangGraph, TypeScript, React, Next.js, FastAPI, Docker, SQLite, GitHub Actions.")


# ---------------------------------------------------------------- contact buttons
def button(label, aria):
    t = f"[ {label} ↗ ]"
    w, h = int(tw(t, 16) + 48), 56
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(aria)}">
<style>text{{font-family:{MONO};white-space:pre}}</style>
<rect width="{w}" height="{h}" fill="{BG}"/><rect x="4.5" y="4.5" width="{w - 9}" height="{h - 9}" fill="none" stroke="{FRAME}" stroke-dasharray="6 5"/>
<text x="{w / 2:.1f}" y="{h / 2 + 6:.1f}" font-size="16" font-weight="700" fill="{GOLD}" text-anchor="middle">{esc(t)}</text>
</svg>"""


# ---------------------------------------------------------------- lab log (daily)
def ago(iso, now):
    d = (now - dt.datetime.fromisoformat(iso.replace("Z", "+00:00"))).total_seconds()
    for s, u in ((86400 * 30, "mo"), (86400 * 7, "w"), (86400, "d"), (3600, "h"), (60, "m")):
        if d >= s:
            return f"{int(d // s)}{u} ago"
    return "just now"


def lab_log(data, user, now=None, rows=6):
    now = now or dt.datetime.now(dt.timezone.utc)
    commits = []
    for r in data["data"]["user"]["repositories"]["nodes"]:
        if r["name"].lower() == user.lower() or not r.get("defaultBranchRef"):
            continue
        for c in r["defaultBranchRef"]["target"]["history"]["nodes"]:
            commits.append((c["committedDate"], r["name"], c["abbreviatedOid"], c["messageHeadline"]))
    commits.sort(reverse=True)
    w = 1118
    h = 112 + 30 * max(1, min(rows, len(commits))) + 46
    out = []
    y = 100
    for i, (when, repo, oid, msg) in enumerate(commits[:rows]):
        msg = msg if len(msg) <= 66 else msg[:65] + "…"
        out.append(f'<text class="ln" style="animation-delay:{.3 + i * .18:.2f}s" x="40" y="{y}" font-size="14" fill="{TEXT}">'
                   f'<tspan fill="{GREEN if i == 0 else FAINT}">● </tspan><tspan fill="{AMBER}">{oid}</tspan>  '
                   f'<tspan fill="{DIM}">{ago(when, now):>8}</tspan>  <tspan fill="{GOLD}">{esc(repo[:34]):<34}</tspan>  {esc(msg)}</text>')
        y += 30
    if not commits:
        out.append(f'<text x="40" y="{y}" font-size="14" fill="{DIM}">quiet week. nothing pushed to a public repo.</text>')
    out.append(f'<text x="{w - 40}" y="{h - 26}" font-size="11" fill="{FAINT}" text-anchor="end">public repos only · redrawn daily · updated {now:%Y-%m-%d}</text>')
    return frame(w, h, "LAB LOG", f"$ git log --all-repos --oneline -{rows}", "\n".join(out),
                 "The latest commits across my public repositories, redrawn daily.")


if __name__ == "__main__":
    if sys.argv[1] == "static":
        for e in EXPERIMENTS:
            save(e["slug"] + ".svg", card(e))
        save("rules.svg", rules())
        for b in BUILT:
            save(b["slug"] + ".svg", built(b))
        save("stack.svg", stack())
        save("btn-linkedin.svg", button("linkedin", "LinkedIn"))
        save("btn-email.svg", button("email", "Email"))
    elif sys.argv[1] == "log":
        user = sys.argv[3] if len(sys.argv) > 3 else "kasheww-nutt"
        save("log.svg", lab_log(json.load(open(sys.argv[2], encoding="utf-8")), user))
