#!/usr/bin/env python3
"""Draw the animated profile SVGs (light + dark) from GitHub data.

Needs GH_TOKEN. Usage:
  build_profile.py static OUTDIR   header and skill loadout (no API calls)
  build_profile.py live OUTDIR     player card, campaign map, achievements
"""
import datetime as dt
import json
import os
import sys
import urllib.request
from html import escape

USER = "aizzat"
XP_PER_LEVEL = 100  # game rule: 1 contribution = 1 XP

THEMES = {
    "dark": dict(bg="#0d1117", panel="#161b22", line="#30363d", text="#e6edf3",
                 muted="#9198a1", blue="#38bdf8", teal="#1fc8c2", gold="#e3b341"),
    "light": dict(bg="#ffffff", panel="#f6f8fa", line="#d1d9e0", text="#1f2328",
                  muted="#59636e", blue="#0369a1", teal="#0f766e", gold="#8a5a00"),
}

CSS = """
text{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,'DejaVu Sans Mono',monospace}
.fade{animation:fade .7s ease-out backwards}
.growx{transform-box:fill-box;transform-origin:left;animation:growx 1.6s cubic-bezier(.2,.7,.2,1) backwards}
.growy{transform-box:fill-box;transform-origin:bottom;animation:growy 1.2s cubic-bezier(.2,.7,.2,1) backwards}
.pulse{animation:pulse 2s ease-in-out infinite}
@keyframes fade{from{opacity:0;transform:translateY(8px)}}
@keyframes growx{from{transform:scaleX(0)}}
@keyframes growy{from{transform:scaleY(0)}}
@keyframes pulse{50%{opacity:.35}}
"""
REDUCED = "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"


def svg(w, h, c, title, body, css=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">'
            f'<title>{escape(title)}</title><style>{CSS}{css}{REDUCED}</style>'
            f'<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="12" fill="{c["bg"]}" stroke="{c["line"]}"/>'
            f'{body}</svg>\n')


def text(x, y, s, fill, size=14, extra=""):
    return f'<text x="{x}" y="{y}" fill="{fill}" font-size="{size}" {extra}>{escape(str(s))}</text>'


def delay(sec):
    return f'style="animation-delay:{sec:.2f}s"'


# ---------------------------------------------------------------- static art
def header(c):
    lines = ["Director, Centre for Innovation & Tech Transfer @ UMPSA",
             "Autonomous Vehicles · Robotics · Physical AI",
             "Teaching robotics with open example code",
             "RM 2.0M+ Research Grants · 100+ Publications · Ex-Intel R&D"]
    n, slot = len(lines), 4
    css = (f".line{{opacity:0;animation:cycle {n*slot}s infinite}}"
           f"@keyframes cycle{{0%{{opacity:0}}3%,{100/n-3:.1f}%{{opacity:1}}{100/n:.1f}%,100%{{opacity:0}}}}"
           ".road{animation:road 1s linear infinite}@keyframes road{to{stroke-dashoffset:-40}}"
           ".bot{animation:drive 14s linear infinite}"
           "@keyframes drive{from{transform:translateX(-90px)}to{transform:translateX(990px)}}"
           ".ping{transform-box:fill-box;transform-origin:center;animation:ping 2s ease-out infinite}"
           "@keyframes ping{from{transform:scale(.2);opacity:.9}to{transform:scale(1);opacity:0}}"
           # with motion reduced, show the first line and park the robot
           "@media (prefers-reduced-motion:reduce){.line:first-of-type{opacity:1}.bot{transform:translateX(760px)}}")
    b = text(450, 62, "Dr. Muhammad Aizzat Zakaria", c["text"], 34, 'text-anchor="middle" font-weight="700"')
    b += text(450, 92, "Autonomous Vehicle Researcher · Associate Professor · Malaysia", c["muted"], 15, 'text-anchor="middle"')
    b += "<g>" + "".join(text(450, 128, "> " + s, c["blue"], 17, f'text-anchor="middle" class="line" {delay(i*slot)}')
                         for i, s in enumerate(lines)) + "</g>"
    b += f'<path d="M20 196H880" stroke="{c["line"]}" stroke-width="2"/>'
    b += f'<path class="road" d="M20 208H880" stroke="{c["muted"]}" stroke-width="2" stroke-dasharray="20 20"/>'
    b += ('<svg x="1" y="130" width="898" height="80" viewBox="0 0 898 80" overflow="hidden"><g class="bot">'
          + "".join(f'<circle class="ping" cx="30" cy="26" r="{r}" fill="none" stroke="{c["teal"]}" {delay(i*.66)}/>'
                    for i, r in enumerate([26, 26, 26]))
          + f'<rect x="4" y="34" width="56" height="22" rx="6" fill="{c["teal"]}"/>'
          f'<rect x="22" y="22" width="16" height="12" rx="3" fill="{c["blue"]}"/>'
          f'<circle class="pulse" cx="52" cy="45" r="4" fill="{c["bg"]}"/>'
          + "".join(f'<circle cx="{x}" cy="59" r="8" fill="{c["text"]}"/><circle cx="{x}" cy="59" r="3" fill="{c["bg"]}"/>'
                    for x in (16, 48))
          + "</g></svg>")
    return svg(900, 224, c, "Dr. Muhammad Aizzat Zakaria, autonomous vehicle researcher. A small robot drives across the banner.", b, css)


def loadout(c):
    slots = [("AUTONOMY", ["Autonomous vehicles", "Physical AI"], c["teal"]),
             ("ROBOTICS", ["Robot software", "Robot modelling"], c["blue"]),
             ("TEACHING", ["Tutorials", "Workshop examples"], c["gold"]),
             ("SOFTWARE", ["Mobile apps", "Web apps"], c["teal"])]
    b = text(24, 34, "SKILL LOADOUT", c["text"], 17, 'font-weight="700"')
    b += text(876, 34, "areas of work, not ratings", c["muted"], 12, 'text-anchor="end"')
    for i, (name, items, col) in enumerate(slots):
        x = 24 + i * 217
        b += f'<g class="fade" {delay(.15+i*.2)}><rect x="{x}" y="52" width="201" height="106" rx="10" fill="{c["panel"]}" stroke="{col}"/>'
        b += text(x + 14, 78, name, col, 13, 'font-weight="700"')
        b += "".join(text(x + 14, 108 + j * 24, s, c["text"], 12) for j, s in enumerate(items))
        b += f'<circle class="pulse" cx="{x+185}" cy="142" r="4" fill="{col}" {delay(i*.4)}/></g>'
    return svg(900, 178, c, "Skill loadout: autonomy, robotics, teaching, software.", b)


# ---------------------------------------------------------------- live data
def gql(query):
    req = urllib.request.Request("https://api.github.com/graphql", json.dumps({"query": query}).encode(),
                                 {"Authorization": "bearer " + os.environ["GH_TOKEN"], "User-Agent": "profile-builder"})
    with urllib.request.urlopen(req, timeout=60) as r:
        out = json.load(r)
    if out.get("errors"):
        sys.exit(f"GraphQL error: {out['errors']}")
    return out["data"]


def fetch():
    now = dt.datetime.now(dt.timezone.utc)
    u = gql(f'query{{user(login:"{USER}"){{createdAt followers{{totalCount}}}}}}')["user"]
    joined = int(u["createdAt"][:4])
    q = "".join(f'y{y}:contributionsCollection(from:"{y}-01-01T00:00:00Z",to:"{y}-12-31T23:59:59Z")'
                '{contributionCalendar{totalContributions}}' for y in range(joined, now.year + 1))
    years = {int(k[1:]): v["contributionCalendar"]["totalContributions"]
             for k, v in gql(f'query{{user(login:"{USER}"){{{q}}}}}')["user"].items()}
    repos, cursor = [], "null"
    while True:
        page = gql(f'query{{user(login:"{USER}"){{repositories(first:100,after:{cursor},ownerAffiliations:OWNER,privacy:PUBLIC)'
                   '{pageInfo{hasNextPage endCursor} nodes{isFork stargazerCount}}}}')["user"]["repositories"]
        repos += page["nodes"]
        if not page["pageInfo"]["hasNextPage"]:
            break
        cursor = json.dumps(page["pageInfo"]["endCursor"])
    prs = gql(f'query{{search(query:"author:{USER} is:pr is:merged is:public",type:ISSUE){{issueCount}}}}')["search"]["issueCount"]
    return dict(joined=joined, today=now.date().isoformat(), year=now.year, years=years,
                total=sum(years.values()), followers=u["followers"]["totalCount"],
                repos=len(repos), original=sum(not r["isFork"] for r in repos),
                stars=sum(r["stargazerCount"] for r in repos), prs=prs)


def player_card(c, d):
    level, into = divmod(d["total"], XP_PER_LEVEL)
    b = f'<rect x="24" y="24" width="112" height="112" rx="14" fill="{c["panel"]}" stroke="{c["teal"]}" stroke-width="2"/>'
    b += text(80, 58, "LEVEL", c["muted"], 13, 'text-anchor="middle"')
    b += text(80, 112, level, c["teal"], 46, 'text-anchor="middle" font-weight="700"')
    b += text(160, 50, "PLAYER: aizzat", c["text"], 20, 'font-weight="700"')
    b += text(160, 76, f'On GitHub since {d["joined"]} · {d["total"]:,} XP (all-time contributions)', c["muted"], 13)
    b += f'<rect x="160" y="94" width="716" height="20" rx="10" fill="{c["panel"]}" stroke="{c["line"]}"/>'
    b += f'<rect class="growx" x="160" y="94" width="{max(20, 716*into/XP_PER_LEVEL):.0f}" height="20" rx="10" fill="{c["teal"]}"/>'
    b += text(160, 134, f"{into} / {XP_PER_LEVEL} XP to level {level+1}", c["blue"], 13)
    b += text(876, 134, "1 contribution = 1 XP · 100 XP = 1 level", c["muted"], 11, 'text-anchor="end"')
    stats = [(f'{d["years"][d["year"]]:,}', f'contributions {d["year"]}'), (d["repos"], "public repos"),
             (d["original"], "non-fork repos"), (d["stars"], "stars incl. forks"),
             (d["prs"], "public PRs merged"), (d["followers"], "followers")]
    for i, (v, label) in enumerate(stats):
        x = 24 + i * 144
        b += (f'<g class="fade" {delay(.3+i*.15)}><rect x="{x}" y="156" width="132" height="70" rx="10" fill="{c["panel"]}" stroke="{c["line"]}"/>'
              + text(x + 66, 188, v, c["text"], 24, 'text-anchor="middle" font-weight="700"')
              + text(x + 66, 212, label, c["muted"], 11, 'text-anchor="middle"') + "</g>")
    b += text(876, 246, f'Updated {d["today"]} · XP includes private contribution counts shown on my profile', c["muted"], 11, 'text-anchor="end"')
    return svg(900, 260, c, f'Level {level}, {d["total"]} all-time contributions.', b)


def campaign(c, d):
    years = sorted(d["years"].items())
    while len(years) > 1 and years[0][1] < 5:  # skip the near-empty early years
        years.pop(0)
    top, slot = max(v for _, v in years) or 1, 852 / len(years)
    b = text(24, 34, "CAMPAIGN MAP · XP EARNED PER YEAR", c["text"], 17, 'font-weight="700"')
    for i, (y, v) in enumerate(years):
        x, h = 24 + i * slot + slot * .18, max(3, 130 * v / top)
        col = c["gold"] if v == top else c["blue"]
        b += f'<rect class="growy" x="{x:.0f}" y="{200-h:.0f}" width="{slot*.64:.0f}" height="{h:.0f}" rx="4" fill="{col}" {delay(i*.15)}/>'
        mid = f'{x+slot*.32:.0f}'
        b += text(mid, f'{192-h:.0f}', f"{v:,}", c["text"], 13, f'text-anchor="middle" class="fade" {delay(.6+i*.15)}')
        b += text(mid, 222, f"{y}*" if y == d["year"] else y, c["muted"], 13, 'text-anchor="middle"')
    b += text(876, 246, f'* year to date, {d["today"]} · gold = best year', c["muted"], 11, 'text-anchor="end"')
    return svg(900, 260, c, "Contributions per year: " + ", ".join(f"{y}: {v}" for y, v in years), b)


def achievements(c, d):
    best = max(d["years"].values())
    badges = [("Veteran", "10+ years on GitHub", d["year"] - d["joined"], 10),
              ("Four Digits", "1,000 all-time XP", d["total"], 1000),
              ("Big Season", "500 XP in one year", best, 500),
              ("Builder", "20 non-fork public repos", d["original"], 20)]
    badges = [(name, rule) for name, rule, value, needed in badges if value >= needed]
    b = text(24, 34, "ACHIEVEMENTS UNLOCKED", c["text"], 17, 'font-weight="700"')
    b += text(876, 34, "page badges based on GitHub data", c["muted"], 11, 'text-anchor="end"')
    for i, (name, rule) in enumerate(badges):
        x = 24 + i * 217
        b += f'<g class="fade" {delay(.1+i*.15)}><rect x="{x}" y="52" width="201" height="70" rx="10" fill="{c["panel"]}" stroke="{c["gold"]}"/>'
        b += text(x + 14, 80, "★ " + name, c["gold"], 13, 'font-weight="700"')
        b += text(x + 14, 104, rule, c["text"], 11) + "</g>"
    return svg(900, 146, c, "Unlocked: " + ", ".join(n for n, _ in badges), b)


def main():
    mode, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    if mode == "static":
        art = {"header": header, "loadout": loadout}
    elif mode == "live":
        data = fetch()
        print(json.dumps(data))
        art = {name: (lambda c, f=f: f(c, data)) for name, f in
               [("player", player_card), ("campaign", campaign), ("achievements", achievements)]}
    else:
        sys.exit(__doc__)
    for name, draw in art.items():
        for theme, colours in THEMES.items():
            with open(os.path.join(out, f"{name}-{theme}.svg"), "w", encoding="utf-8") as f:
                f.write(draw(colours))


if __name__ == "__main__":
    main()
