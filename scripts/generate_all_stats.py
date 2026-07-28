#!/usr/bin/env python3
"""
Génère 4 SVGs de statistiques GitHub avec Tokyo Night dark theme.
API GraphQL directe avec GH_TOKEN → inclut TOUS les dépôts (privés + publics).
"""

import os, sys
import requests
from datetime import datetime
from collections import defaultdict

TOKEN    = os.environ.get("GH_TOKEN", "")
USERNAME = "ouzfeya7"
GQL      = "https://api.github.com/graphql"

# ── Tokyo Night palette ────────────────────────────────────────────────────────
BG   = "#0d1117"
BG2  = "#161b22"
CARD = "#1a1b2e"
BORD = "#30363d"
TEXT = "#c0caf5"
DIM  = "#565f89"
BLUE = "#7aa2f7"
PURP = "#bb9af7"
GREE = "#9ece6a"
ORAN = "#ff9e64"
RED  = "#f7768e"
CYAN = "#7dcfff"
YELL = "#e0af68"
FONT = "'Segoe UI', system-ui, -apple-system, sans-serif"

QUERY = """
query($username: String!) {
  user(login: $username) {
    name
    login
    followers { totalCount }
    following { totalCount }
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      restrictedContributionsCount
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
    repositories(
      first: 100
      ownerAffiliations: OWNER
      orderBy: { field: STARGAZERS, direction: DESC }
    ) {
      totalCount
      nodes {
        stargazerCount
        forkCount
        languages(first: 10, orderBy: { field: SIZE, direction: DESC }) {
          edges {
            size
            node { name color }
          }
        }
      }
    }
  }
}
"""

def fetch():
    r = requests.post(
        GQL,
        json={"query": QUERY, "variables": {"username": USERNAME}},
        headers={"Authorization": f"Bearer {TOKEN}"},
        timeout=30,
    )
    r.raise_for_status()
    d = r.json()
    if "errors" in d:
        print("GraphQL errors:", d["errors"], file=sys.stderr)
        sys.exit(1)
    return d["data"]["user"]

def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

# ── stats.svg ──────────────────────────────────────────────────────────────────
def stats_svg(u):
    c       = u["contributionsCollection"]
    repos   = u["repositories"]
    commits = c["totalCommitContributions"]
    prs     = c["totalPullRequestContributions"]
    issues  = c["totalIssueContributions"]
    stars   = sum(r["stargazerCount"] for r in repos["nodes"])
    forks   = sum(r["forkCount"]      for r in repos["nodes"])
    total   = c["contributionCalendar"]["totalContributions"]
    restr   = c["restrictedContributionsCount"]
    name    = esc(u["name"] or u["login"])
    follw   = u["followers"]["totalCount"]
    follwg  = u["following"]["totalCount"]
    n_repos = repos["totalCount"]

    W, H = 860, 180

    STATS = [
        (commits, "Commits",       BLUE, "M6.5 1C6.5 .448 6.052 0 5.5 0s-1 .448-1 1v2.5H2A2 2 0 000 5.5v5A2 2 0 002 12.5h10a2 2 0 002-2v-5A2 2 0 0012 3.5H9.5V1c0-.552-.448-1-1-1S7.5.448 7.5 1v2.5h-1V1z"),
        (prs,     "Pull Requests", PURP, "M7.177 3.073L9.573.677A.25.25 0 0110 .854v4.792a.25.25 0 01-.427.177L7.177 3.427a.25.25 0 010-.354zM3.75 2.5a.75.75 0 100 1.5.75.75 0 000-1.5zm-2.25.75a2.25 2.25 0 113 2.122v5.256a2.251 2.251 0 11-1.5 0V5.372A2.25 2.25 0 011.5 3.25zM11 2.5h-1V4h1a1 1 0 011 1v5.628a2.251 2.251 0 101.5 0V5A2.5 2.5 0 0011 2.5zm1 10.25a.75.75 0 111.5 0 .75.75 0 01-1.5 0zM3.75 12a.75.75 0 100 1.5.75.75 0 000-1.5z"),
        (issues,  "Issues",        RED,  "M8 9.5a1.5 1.5 0 100-3 1.5 1.5 0 000 3z M8 0a8 8 0 100 16A8 8 0 008 0zM1.5 8a6.5 6.5 0 1113 0 6.5 6.5 0 01-13 0z"),
        (stars,   "Stars",         YELL, "M8 .25a.75.75 0 01.673.418l1.882 3.815 4.21.612a.75.75 0 01.416 1.279l-3.046 2.97.719 4.192a.75.75 0 01-1.088.791L8 12.347l-3.766 1.98a.75.75 0 01-1.088-.79l.72-4.194L.818 6.374a.75.75 0 01.416-1.28l4.21-.611L7.327.668A.75.75 0 018 .25z"),
        (n_repos, "Repos",         CYAN, "M2 2.5A2.5 2.5 0 014.5 0h8.75a.75.75 0 01.75.75v12.5a.75.75 0 01-.75.75h-2.5a.75.75 0 010-1.5h1.75v-2h-8a1 1 0 00-.714 1.7.75.75 0 01-1.072 1.05A2.495 2.495 0 012 11.5v-9zm10.5-1V9h-8c-.356 0-.694.074-1 .208V2.5a1 1 0 011-1h8z"),
    ]

    n = len(STATS)
    col_w = W / n

    cols = []
    for i, (val, label, col, icon_path) in enumerate(STATS):
        cx = i * col_w + col_w / 2
        ix = cx - 8
        iy = 88

        if i > 0:
            cols.append(f'<line x1="{i*col_w:.0f}" y1="78" x2="{i*col_w:.0f}" y2="148" stroke="{BORD}"/>')

        cols.append(
            f'<g transform="translate({ix:.1f},{iy}) scale(1.1)" opacity="0.6">'
            f'<path fill="{col}" d="{icon_path}"/></g>'
        )
        cols.append(
            f'<text x="{cx:.1f}" y="120" text-anchor="middle" '
            f'font-size="30" font-weight="700" fill="{col}" letter-spacing="-0.5">{val:,}</text>'
        )
        cols.append(
            f'<text x="{cx:.1f}" y="140" text-anchor="middle" font-size="11" fill="{DIM}">{label}</text>'
        )

    private_badge = ""
    if restr > 0:
        bx = W - 210
        private_badge = (
            f'<rect x="{bx}" y="44" width="190" height="20" rx="10" fill="#1a2a1a" stroke="{GREE}" stroke-width="0.5"/>'
            f'<text x="{bx+95}" y="58" text-anchor="middle" font-size="10.5" fill="{GREE}">🔒 {restr} contributions privées</text>'
        )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
  <linearGradient id="sbg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="{BG}"/>
    <stop offset="100%" stop-color="{BG2}"/>
  </linearGradient>
  <linearGradient id="hline" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="{BLUE}" stop-opacity="0.8"/>
    <stop offset="100%" stop-color="{PURP}" stop-opacity="0.8"/>
  </linearGradient>
</defs>
<style>text{{font-family:{FONT}}}
</style>
<rect width="{W}" height="{H}" rx="12" fill="url(#sbg)" stroke="{BORD}"/>
<rect x="0" y="70" width="{W}" height="2" fill="url(#hline)" opacity="0.3"/>
<text x="20" y="33" font-size="20" font-weight="700" fill="{TEXT}">{name}</text>
<text x="20" y="53" font-size="12" fill="{DIM}">@{USERNAME}  ·  {follw} followers  ·  {follwg} following  ·  {total} contributions cette année</text>
{private_badge}
<rect x="0" y="68" width="{W}" height="1" fill="{BORD}"/>
{''.join(cols)}
<rect x="0" y="150" width="{W}" height="1" fill="{BORD}"/>
<text x="20" y="167" font-size="11" fill="{DIM}">⭐ {stars} étoiles reçues  ·  🍴 {forks} forks  ·  📁 {n_repos} dépôts</text>
</svg>"""

# ── languages.svg ──────────────────────────────────────────────────────────────
def languages_svg(u):
    lang_data = defaultdict(lambda: {"size": 0, "color": "#888"})
    for repo in u["repositories"]["nodes"]:
        for edge in repo["languages"]["edges"]:
            ln = edge["node"]["name"]
            lang_data[ln]["size"] += edge["size"]
            if edge["node"]["color"]:
                lang_data[ln]["color"] = edge["node"]["color"]

    total_b = sum(v["size"] for v in lang_data.values()) or 1
    langs   = sorted(lang_data.items(), key=lambda x: -x[1]["size"])[:10]

    W     = 860
    PAD   = 20
    ROW_H = 34
    BAR_H = 6
    H     = 56 + len(langs) * ROW_H + PAD

    # Stacked color strip
    strip_w = W - 2 * PAD
    strip_x = PAD
    strip = [f'<rect x="{PAD}" y="36" width="{strip_w}" height="10" rx="5" fill="{BORD}"/>']
    for lang, info in langs:
        sw = strip_w * info["size"] / total_b
        strip.append(
            f'<rect x="{strip_x:.1f}" y="36" width="{max(sw,1):.1f}" height="10" fill="{info["color"]}"/>'
        )
        strip_x += sw
    # Re-clip corners
    strip.insert(0, f'<clipPath id="sc"><rect x="{PAD}" y="36" width="{strip_w}" height="10" rx="5"/></clipPath>')
    strip_body = [strip[0]] + [f'<g clip-path="url(#sc)">' + ''.join(strip[1:]) + '</g>']

    rows = []
    for i, (lang, info) in enumerate(langs):
        pct   = info["size"] / total_b * 100
        bfw   = strip_w * pct / 100
        y     = 60 + i * ROW_H
        rows += [
            f'<circle cx="{PAD+5}" cy="{y+9}" r="5.5" fill="{info["color"]}"/>',
            f'<text x="{PAD+18}" y="{y+14}" font-size="13" fill="{TEXT}">{esc(lang)}</text>',
            f'<text x="{W-PAD}" y="{y+14}" font-size="12" fill="{DIM}" text-anchor="end">{pct:.1f}%</text>',
            f'<rect x="{PAD}" y="{y+22}" width="{strip_w}" height="{BAR_H}" rx="3" fill="{BORD}"/>',
            f'<rect x="{PAD}" y="{y+22}" width="{bfw:.1f}" height="{BAR_H}" rx="3" fill="{info["color"]}" opacity="0.85"/>',
        ]

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<style>text{{font-family:{FONT}}}</style>
<rect width="{W}" height="{H}" rx="12" fill="{BG}" stroke="{BORD}"/>
<text x="{PAD}" y="24" font-size="15" font-weight="700" fill="{TEXT}">Langages utilisés</text>
{''.join(strip_body)}
{''.join(rows)}
</svg>"""

# ── calendar.svg ───────────────────────────────────────────────────────────────
def calendar_svg(u):
    c      = u["contributionsCollection"]
    weeks  = c["contributionCalendar"]["weeks"]
    total  = c["contributionCalendar"]["totalContributions"]
    restr  = c["restrictedContributionsCount"]

    all_days = [d for w in weeks for d in w["contributionDays"]]
    max_c    = max((d["contributionCount"] for d in all_days), default=1) or 1

    CELL, GAP = 12, 3
    PAD_L, PAD_T = 30, 58
    n_weeks = len(weeks)
    W = PAD_L + n_weeks * (CELL + GAP) + 24
    H = PAD_T + 7 * (CELL + GAP) + 34

    LVL = ["#1a2030", "#0e4429", "#006d32", "#26a641", "#39d353"]

    cells, month_labels = [], {}
    for wi, week in enumerate(weeks):
        for day in week["contributionDays"]:
            dt  = datetime.fromisoformat(day["date"])
            di  = dt.weekday()
            cnt = day["contributionCount"]
            lvl = 0 if cnt == 0 else min(int(cnt / max_c * 3) + 1, 4)
            x = PAD_L + wi * (CELL + GAP)
            y = PAD_T + di * (CELL + GAP)
            cells.append(
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{LVL[lvl]}"/>'
            )
            if dt.day == 1:
                month_labels[wi] = dt.strftime("%b")

    mlabels = [
        f'<text x="{PAD_L + wi*(CELL+GAP)}" y="{PAD_T-6}" font-size="10" fill="{DIM}">{m}</text>'
        for wi, m in month_labels.items()
    ]
    dlabels = [
        f'<text x="{PAD_L-6}" y="{PAD_T + i*(CELL+GAP)+CELL}" font-size="9" fill="{DIM}" text-anchor="end">{d}</text>'
        for i, d in enumerate(["L","M","M","J","V","S","D"])
    ]

    note = f" (dont {restr} contributions privées)" if restr > 0 else ""

    # Legend
    legend_x = W - 24 - 5 * (CELL + GAP)
    legend = [f'<text x="{legend_x - 8}" y="{H-8}" font-size="9" fill="{DIM}" text-anchor="end">moins</text>']
    for li, lc in enumerate(LVL):
        lx = legend_x + li * (CELL + GAP)
        legend.append(f'<rect x="{lx}" y="{H-17}" width="{CELL}" height="{CELL}" rx="2" fill="{lc}"/>')
    legend.append(f'<text x="{legend_x + 5*(CELL+GAP) + 3}" y="{H-8}" font-size="9" fill="{DIM}">plus</text>')

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<style>text{{font-family:{FONT}}}</style>
<rect width="{W}" height="{H}" rx="12" fill="{BG}" stroke="{BORD}"/>
<text x="18" y="26" font-size="15" font-weight="700" fill="{TEXT}">Calendrier de contributions</text>
<text x="18" y="44" font-size="12" fill="{DIM}"><tspan fill="{GREE}" font-weight="600">{total}</tspan> contributions{esc(note)}</text>
{''.join(mlabels)}
{''.join(dlabels)}
{''.join(cells)}
{''.join(legend)}
</svg>"""

# ── activity.svg ───────────────────────────────────────────────────────────────
def activity_svg(u):
    c       = u["contributionsCollection"]
    all_d   = [d for w in c["contributionCalendar"]["weeks"] for d in w["contributionDays"]]
    days    = all_d[-30:]
    total   = c["contributionCalendar"]["totalContributions"]
    commits = c["totalCommitContributions"]
    prs     = c["totalPullRequestContributions"]
    issues  = c["totalIssueContributions"]
    restr   = c["restrictedContributionsCount"]

    W, H = 860, 180
    PL, PR, PT, PB = 10, 10, 52, 38
    baw = W - PL - PR
    bah = H - PT - PB

    n = len(days)
    slot = baw / n
    gap  = slot * 0.2
    bw   = slot - gap
    max_c = max((d["contributionCount"] for d in days), default=1) or 1

    LVL = {0:"#1a2030", 1:"#0e4429", 2:"#006d32", 3:"#26a641", 4:"#39d353"}
    def lvl(c):
        if c == 0: return 0
        r = c / max_c
        return 1 if r <= .25 else 2 if r <= .5 else 3 if r <= .75 else 4

    bars, labels = [], []
    for i, d in enumerate(days):
        cnt = d["contributionCount"]
        x   = PL + i * slot + gap / 2
        bh  = max((cnt / max_c) * bah, 2) if cnt else 2
        by  = PT + bah - bh
        bars.append(
            f'<rect x="{x:.1f}" y="{by:.1f}" width="{bw:.1f}" height="{bh:.1f}" '
            f'fill="{LVL[lvl(cnt)]}" rx="2"/>'
        )
        if i % 5 == 0 or i == n - 1:
            labels.append(
                f'<text x="{x+bw/2:.1f}" y="{PT+bah+16}" text-anchor="middle" '
                f'font-size="8.5" fill="{DIM}">{d["date"][5:]}</text>'
            )

    priv = f" (dont {restr} privées)" if restr > 0 else ""

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
  <linearGradient id="abg" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="{BG}"/>
    <stop offset="100%" stop-color="{BG2}"/>
  </linearGradient>
  <linearGradient id="aline" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="{GREE}" stop-opacity="0.7"/>
    <stop offset="100%" stop-color="{CYAN}" stop-opacity="0.7"/>
  </linearGradient>
</defs>
<style>text{{font-family:{FONT}}}</style>
<rect width="{W}" height="{H}" rx="12" fill="url(#abg)" stroke="{BORD}"/>
<rect x="{PL}" y="{PT}" width="{baw}" height="{bah}" rx="4" fill="{CARD}" opacity="0.35"/>
<rect x="0" y="{PT+bah}" width="{W}" height="1" fill="url(#aline)" opacity="0.4"/>
<text x="14" y="24" font-size="14" font-weight="700" fill="{TEXT}">Activité — 30 derniers jours</text>
<text x="14" y="41" font-size="11.5" fill="{DIM}">
  <tspan fill="{GREE}" font-weight="600">{total}</tspan> contributions au total{esc(priv)}  ·  
  <tspan fill="{BLUE}" font-weight="600">{commits}</tspan> commits  ·  
  <tspan fill="{PURP}" font-weight="600">{prs}</tspan> pull requests  ·  
  <tspan fill="{RED}" font-weight="600">{issues}</tspan> issues
</text>
{''.join(bars)}
{''.join(labels)}
</svg>"""

# ── main ───────────────────────────────────────────────────────────────────────
def main():
    if not TOKEN:
        print("GH_TOKEN manquant", file=sys.stderr)
        sys.exit(1)

    print(f"📊 Génération des statistiques GitHub pour @{USERNAME}...")
    u = fetch()
    os.makedirs("metrics", exist_ok=True)

    for name_s, fn in [
        ("stats",     stats_svg),
        ("languages", languages_svg),
        ("calendar",  calendar_svg),
        ("activity",  activity_svg),
    ]:
        path = f"metrics/{name_s}.svg"
        with open(path, "w", encoding="utf-8") as f:
            f.write(fn(u))
        print(f"  ✅ {path}")

    c = u["contributionsCollection"]
    print(f"\n📈 Résumé :")
    print(f"   Commits       : {c['totalCommitContributions']}")
    print(f"   Pull Requests : {c['totalPullRequestContributions']}")
    print(f"   Issues        : {c['totalIssueContributions']}")
    print(f"   Total contribs: {c['contributionCalendar']['totalContributions']}")
    print(f"   Privées inclus: {c['restrictedContributionsCount']}")


if __name__ == "__main__":
    main()
