#!/usr/bin/env python3
"""Render the profile README's cards as animated SVGs into cards/.

Each card is a standalone SVG shown through <img>, so it only uses what GitHub allows
there: inline CSS animations and fonts embedded as data URIs (no JS, no external requests).
Fonts (Instrument Serif, Geist, Geist Mono; SIL OFL) are subset WOFFs in fonts/.

Reads data/profile.json (scripts/fetch_data.py) and assets/portrait.txt (scripts/make_portrait.py).
Standard library only. Set STATIC=1 to render every animation at its end state (for previews).
"""
import base64
import datetime
import json
import os
from html import escape

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DATA = json.load(open(os.path.join(ROOT, "data", "profile.json")))
PORTRAIT = open(os.path.join(ROOT, "assets", "portrait.txt")).read().rstrip("\n").split("\n")
OUT = os.path.join(ROOT, "cards")
FONTS = os.path.join(ROOT, "fonts")

# ---- edit these: your words -------------------------------------------------
FIRST, LAST = "Ngawang", "Dorji"
KICKER = "SOFTWARE ENGINEER AT 21 TECH"
TAGLINE = ["I build web and mobile products from Thimphu, Bhutan,", "with Next.js, NestJS and React Native."]
LINK_TEXT, LINK_URL = "github.com/NovaIsCoding", "https://github.com/NovaIsCoding"
TILES = [  # label, big text, description, background, text colour, link
    ("BUILD", None, "across Census-Pro, Attendance-Pro, BhutanApp and LuckyPem.", "#111111", "#ffffff", "https://github.com/Census-Pro"),
    ("STACK", "Full stack", "Next.js, NestJS and React Native, from the API to the app.", "#2f55ff", "#ffffff", "https://github.com/NovaIsCoding?tab=repositories"),
    ("BEYOND", "Design", "UI/UX, gaming and gadget reviews when I'm not shipping.", "#cdd8ff", "#111111", "https://github.com/NovaIsCoding"),
]
CODING_TITLE = "What I'm coding"
ORG_REPOS = 37

# ---- tokens -----------------------------------------------------------------
PAPER, PAPER_DEEP, INK, MUTED, RULE = "#f3f3f1", "#e2e2de", "#111111", "#6e6e73", "#dcdcd7"
ACC = "#2f55ff"
HEAT = {"NONE": PAPER_DEEP, "FIRST_QUARTILE": "#d3dcff", "SECOND_QUARTILE": "#9db3ff",
        "THIRD_QUARTILE": "#5c7dff", "FOURTH_QUARTILE": "#1f3fd6"}
W, GAP = 880, 12
HG = 16                    # horizontal gap between the three cards in a row
CW = (W - 2 * HG) / 3      # drawn card width; cell stays W/3 so GitHub tiles them exactly


def cell_offset(i):
    return i * HG / 3
SERIF = "'Instrument Serif', Georgia, serif"
SANS = "Geist, system-ui, -apple-system, sans-serif"
MONO = "'Geist Mono', ui-monospace, SFMono-Regular, Menlo, monospace"
FONT_FILES = {
    "serif": ("Instrument Serif", "normal", 400, "serif-400.woff"),
    "serif-i": ("Instrument Serif", "italic", 400, "serif-italic.woff"),
    "sans": ("Geist", "normal", 400, "geist-400.woff"),
    "sans-b": ("Geist", "normal", 600, "geist-600.woff"),
    "mono": ("Geist Mono", "normal", 400, "geistmono-400.woff"),
}
CSS = """
@keyframes rise{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:none}}
@keyframes fade{from{opacity:0}to{opacity:1}}
@keyframes grow{from{transform:scaleY(0)}to{transform:scaleY(1)}}
@keyframes pop{0%{opacity:0;transform:scale(.3)}70%{opacity:1;transform:scale(1.15)}100%{opacity:1;transform:none}}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.25}}
@keyframes nudge{0%,100%{transform:none}50%{transform:translateX(4px)}}
@keyframes ring{0%{opacity:.7;transform:scale(.2)}100%{opacity:0;transform:scale(2.4)}}
.r{opacity:0;animation:rise .8s cubic-bezier(.2,.7,.2,1) both;transform-box:fill-box}
.f{opacity:0;animation:fade .9s ease-out both}
.g{transform-box:fill-box;transform-origin:bottom;transform:scaleY(0);animation:grow .8s cubic-bezier(.2,.7,.2,1) both}
.p{opacity:0;transform-box:fill-box;transform-origin:center;animation:pop .4s ease-out both}
.live{animation:pulse 1.6s ease-in-out infinite}
.n{transform-box:fill-box;animation:nudge 1.8s ease-in-out infinite}
.rg{opacity:0;transform-box:fill-box;transform-origin:center;animation:ring 1s ease-out both}
@media (prefers-reduced-motion: reduce){.r,.f,.g,.p,.live,.n,.rg{animation:none!important;opacity:1!important;transform:none!important}.rg{display:none}}
"""


def font_face(keys):
    out = []
    for k in keys:
        fam, style, weight, fn = FONT_FILES[k]
        b64 = base64.b64encode(open(os.path.join(FONTS, fn), "rb").read()).decode()
        out.append(f"@font-face{{font-family:'{fam}';font-style:{style};font-weight:{weight};"
                   f"src:url(data:font/woff;base64,{b64}) format('woff')}}")
    return "".join(out)


def svg(w, h, body, fonts, label, bottom=GAP):
    css = font_face(fonts) + CSS
    if os.environ.get("STATIC"):
        css += ".r,.f,.g,.p,.live,.n{animation:none!important;opacity:1!important;transform:none!important}.rg{display:none}"
    h += bottom
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.3f}" height="{h}" viewBox="0 0 {w:.3f} {h}" '
            f'role="img" aria-label="{escape(label)}"><title>{escape(label)}</title><style>{css}</style>{body}</svg>')


def write(name, content):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, name), "w") as f:
        f.write(content)
    print(f"wrote cards/{name} ({len(content) // 1024} KB)")


def d(s):
    return f'style="animation-delay:{s:.2f}s"'


def wrap(text, n):
    lines, line = [], ""
    for word in text.split():
        if line and len(line) + 1 + len(word) > n:
            lines.append(line)
            line = word
        else:
            line = f"{line} {word}".strip()
    return lines + ([line] if line else [])


def fmt(n):
    return f"{int(n):,}"


# ---- hero -------------------------------------------------------------------
def hero():
    h = 432
    b = [f'<rect width="{W}" height="{h}" rx="20" fill="{PAPER}"/>']
    b.append(f'<rect class="p live" x="32" y="52" width="10" height="10" rx="2" fill="{ACC}" {d(0.1)}/>')
    b.append(f'<text class="f" x="52" y="62" font-family="{MONO}" font-size="13" letter-spacing="1.6" fill="{INK}" {d(0.1)}>{escape(KICKER)}</text>')
    b.append(f'<text class="r" x="30" y="184" font-family="{SERIF}" font-size="124" fill="{INK}" {d(0.25)}>{escape(FIRST)}</text>')
    cut = len(LAST) - 2
    b.append(f'<text class="r" x="34" y="294" font-family="{SERIF}" font-style="italic" font-size="124" fill="{INK}" {d(0.45)}>'
             f'{escape(LAST[:cut])}<tspan fill="{ACC}">{escape(LAST[cut:])}</tspan></text>')
    for i, line in enumerate(TAGLINE):
        b.append(f'<text class="r" x="34" y="{346 + i * 28}" font-family="{SANS}" font-size="19" fill="{INK}" {d(0.7 + i * 0.1)}>{escape(line)}</text>')
    b.append(f'<a href="{LINK_URL}"><text class="r" x="34" y="{346 + len(TAGLINE) * 28 + 12}" font-family="{MONO}" font-size="14" fill="{INK}" {d(1.0)}>'
             f'{escape(LINK_TEXT)}  <tspan fill="{ACC}">↗</tspan></text></a>')
    # ASCII portrait, right side, revealed line by line from the top
    cw, ch, fs = 2.27, 4.0, 3.75
    px = W - 32 - 150 * cw
    py = (h - len(PORTRAIT) * ch) / 2 + 10
    for i, line in enumerate(PORTRAIT):
        if line.strip():
            b.append(f'<text class="f" x="{px:.2f}" y="{py + i * ch:.2f}" font-family="{MONO}" font-size="{fs}" '
                     f'fill="{INK}" xml:space="preserve" {d(0.4 + i * 0.022)}>{escape(line)}</text>')
    return svg(W, h, "".join(b), ["serif", "serif-i", "sans", "mono"], f"{FIRST} {LAST}. {KICKER.title()}.")


# ---- heatmap ----------------------------------------------------------------
def heatmap():
    h = 257
    weeks = DATA["weeks"]
    b = [f'<rect width="{W}" height="{h}" rx="20" fill="{PAPER}"/>']
    b.append(f'<text class="f" x="32" y="62" font-family="{SERIF}" font-size="38" fill="{INK}">Every day, '
             f'<tspan font-style="italic" fill="{ACC}">in blue</tspan></text>')
    gx, gy = 32, 88
    step = (W - 64) / len(weeks)
    size = step - 3
    last_month = None
    for wi, wk in enumerate(weeks):
        for di, day in enumerate(wk):
            col = HEAT.get(day["level"], PAPER_DEEP)
            b.append(f'<rect class="p" x="{gx + wi * step:.1f}" y="{gy + di * step:.1f}" width="{size:.1f}" height="{size:.1f}" rx="3" '
                     f'fill="{col}" {d(0.3 + wi * 0.028 + di * 0.012)}><title>{day["date"]}: {day["n"]}</title></rect>')
        m = datetime.date.fromisoformat(wk[0]["date"]).strftime("%b")
        if m != last_month and wi < len(weeks) - 3:
            b.append(f'<text class="f" x="{gx + wi * step:.1f}" y="{gy + 7 * step + 22:.1f}" font-family="{MONO}" font-size="11" fill="{MUTED}" {d(2.0)}>{m}</text>')
            last_month = m
    b.append(f'<text class="f" x="{W - 32}" y="58" text-anchor="end" font-family="{MONO}" font-size="13" letter-spacing="1.6" fill="{MUTED}">REFRESHED DAILY</text>')
    return svg(W, h, "".join(b), ["serif", "serif-i", "mono"], f"Contribution graph: {fmt(DATA['total'])} contributions in the last year")


# ---- activity ---------------------------------------------------------------
def activity():
    h = 352
    b = [f'<rect width="{W}" height="{h}" rx="20" fill="{PAPER}"/>']
    b.append(f'<text class="f" x="32" y="52" font-family="{MONO}" font-size="12" letter-spacing="1.6" fill="{MUTED}">THE LAST 12 MONTHS ON GITHUB</text>')
    b.append(f'<text class="r" x="32" y="104" font-family="{SERIF}" font-size="60" fill="{INK}" {d(0.1)}>{fmt(DATA["total"])} '
             f'<tspan font-style="italic">contributions</tspan></text>')
    months = DATA["months"]
    mx = max(m["count"] for m in months) or 1
    cx0, cw_total, base, maxh = 32, 520, 300, 140
    bw = 36
    stp = (cw_total - bw) / (len(months) - 1)
    for i, m in enumerate(months):
        bh = max(4, m["count"] / mx * maxh)
        x = cx0 + i * stp
        peak, partial = m["count"] == mx, i == len(months) - 1
        fill = ACC if peak else ("#c9c9c3" if partial else INK)
        b.append(f'<rect class="g" x="{x:.1f}" y="{base - bh:.1f}" width="{bw}" height="{bh:.1f}" rx="4" fill="{fill}" {d(0.3 + i * 0.06)}><title>{m["month"]}: {m["count"]}</title></rect>')
        if peak:
            b.append(f'<text class="f" x="{x + bw / 2:.1f}" y="{base - bh - 10:.1f}" text-anchor="middle" font-family="{MONO}" font-size="12" fill="{ACC}" {d(1.2)}>{fmt(m["count"])}</text>')
        lab = datetime.date.fromisoformat(m["month"] + "-01").strftime("%b")
        b.append(f'<text class="f" x="{x + bw / 2:.1f}" y="{base + 24}" text-anchor="middle" font-family="{MONO}" font-size="11" fill="{MUTED}" {d(1.0)}>{lab}</text>')
    stats = [(f"{DATA['streak']} days", "current streak"),
             (f"{DATA['active_days']} / {DATA['total_days']}", "days with a commit"),
             (fmt(DATA["busiest"]), "on the busiest day")]
    sx = 630
    for i, (big, small) in enumerate(stats):
        y = 118 + i * 74
        if i:
            b.append(f'<line class="f" x1="{sx}" y1="{y - 44}" x2="{W - 32}" y2="{y - 44}" stroke="{RULE}" {d(0.6 + i * 0.15)}/>')
        b.append(f'<text class="r" x="{sx}" y="{y}" font-family="{SERIF}" font-size="46" fill="{INK}" {d(0.6 + i * 0.15)}>{escape(big)}</text>')
        b.append(f'<text class="r" x="{sx}" y="{y + 24}" font-family="{SANS}" font-size="14" fill="{MUTED}" {d(0.7 + i * 0.15)}>{escape(small)}</text>')
    return svg(W, h, "".join(b), ["serif", "serif-i", "sans", "mono"], f"{fmt(DATA['total'])} contributions in the last year, {DATA['streak']}-day streak")


# ---- tiles ------------------------------------------------------------------
def tile(i):
    label, big, desc, bg, fg, link = TILES[i]
    w, h = CW, 222
    off = cell_offset(i)
    if big is None:
        # Hard-coded for now: the CI token can't read the orgs, so the fetched count is 0.
        # Switch back to DATA["org_repos"] once ORG_TOKEN works.
        big = f"{ORG_REPOS} repos"
    edge = ' stroke="#3a3a40" stroke-width="1"' if bg == "#111111" else ""   # keeps the dark tile visible in dark mode
    b = [f'<a href="{link}"><rect x="0.5" y="0.5" width="{w - 1:.3f}" height="{h - 1}" rx="20" fill="{bg}"{edge}/>']
    b.append(f'<circle class="rg" cx="{w - 40:.1f}" cy="{h - 30}" r="80" fill="none" stroke="{fg}" stroke-opacity=".5" {d(0.3)}/>')
    b.append(f'<text class="f" x="28" y="40" font-family="{MONO}" font-size="13" letter-spacing="1.6" fill="{fg}">{escape(label)}</text>')
    b.append(f'<text class="n" x="{w - 28:.1f}" y="41" text-anchor="end" font-family="{SANS}" font-size="16" fill="{fg}">→</text>')
    b.append(f'<text class="r" x="28" y="104" font-family="{SERIF}" font-size="52" fill="{fg}" {d(0.2 + i * 0.1)}>{escape(big)}</text>')
    for k, line in enumerate(wrap(desc, 34)):
        b.append(f'<text class="r" x="28" y="{142 + k * 22}" font-family="{SANS}" font-size="15" fill="{fg}" {d(0.4 + i * 0.1 + k * 0.05)}>{escape(line)}</text>')
    b.append("</a>")
    body = f'<g transform="translate({off:.3f} 0)">{"".join(b)}</g>'
    return svg(W / 3, h, body, ["serif", "sans", "mono"], f"{label}: {big}. {desc}")


# ---- coding title + repo cards ---------------------------------------------
def coding_title():
    h = 64
    b = (f'<rect width="{W}" height="{h}" rx="20" fill="{PAPER}"/>'
         f'<text class="f" x="32" y="45" font-family="{SERIF}" font-size="38" fill="{INK}">{escape(CODING_TITLE)}</text>')
    return svg(W, h, b, ["serif"], CODING_TITLE)


def repo_card(r, i):
    w, h = CW, 188
    b = [f'<a href="{r["url"]}"><rect width="{w:.3f}" height="{h}" rx="20" fill="{PAPER}"/>']
    b.append(f'<rect class="p" x="28" y="30" width="10" height="10" rx="2" fill="{ACC}"/>')
    b.append(f'<text class="r" x="48" y="40" font-family="{SANS}" font-weight="600" font-size="20" fill="{INK}">{escape(r["name"])}</text>')
    desc = r["desc"] or (f"A {r['lang']} project." if r["lang"] else "Open on GitHub.")
    for k, line in enumerate(wrap(desc, 36)[:3]):
        b.append(f'<text class="r" x="28" y="{74 + k * 22}" font-family="{SANS}" font-size="15" fill="#3a3a3c" {d(0.2 + k * 0.08)}>{escape(line)}</text>')
    foot = " · ".join(x for x in [r["lang"], f"★ {r['stars']}" if r["stars"] else ""] if x) or "GitHub"
    b.append(f'<text class="f" x="28" y="{h - 28}" font-family="{MONO}" font-size="13" fill="{MUTED}">{escape(foot)}</text></a>')
    body = f'<g transform="translate({cell_offset(i):.3f} 0)">{"".join(b)}</g>'
    return svg(W / 3, h, body, ["sans", "sans-b", "mono"], f"{r['name']}: {desc}")


if __name__ == "__main__":
    write("hero.svg", hero())
    write("heatmap.svg", heatmap())
    write("activity.svg", activity())
    for i, name in enumerate(["build", "stack", "beyond"]):
        write(f"{name}.svg", tile(i))
    write("title-coding.svg", coding_title())
    for i, r in enumerate(DATA["repos"]):
        write(f"repo-{r['name']}.svg", repo_card(r, i))
