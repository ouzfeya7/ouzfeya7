#!/usr/bin/env python3
"""
Génère 4 SVGs de statistiques GitHub avec Tokyo Night dark theme.
Design "Bento Box" pour une lisibilité parfaite (1:1 native scale).
"""

import os, sys
import requests
from datetime import datetime
from collections import defaultdict

TOKEN    = os.environ.get("GH_TOKEN", "")
USERNAME = "ouzfeya7"
GQL      = "https://api.github.com/graphql"

# ── Tokyo Night palette ────────────────────────────────────────────────────────
BG   = "#161b22"  # Fond légèrement plus clair pour détacher du noir de GitHub
BG2  = "#0d1117"
CARD = "#21262d"
BORD = "#30363d"
TEXT = "#c9d1d9"
DIM  = "#8b949e"
BLUE = "#58a6ff"
PURP = "#bc8cff"
GREE = "#3fb950"
ORAN = "#ff7b72"
RED  = "#f85149"
CYAN = "#38bdae"
YELL = "#d2a8ff"
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
    total   = c["contributionCalendar"]["totalContributions"]
    follw   = u["followers"]["totalCount"]
    n_repos = repos["totalCount"]
    name    = esc(u["name"] or u["login"])

    # Format optimisé pour être affiché à 48% de largeur (donc 440px réel)
    W, H = 440, 240

    STATS = [
        (commits, "Commits",       BLUE, "M6.5 1C6.5 .448 6.052 0 5.5 0s-1 .448-1 1v2.5H2A2 2 0 000 5.5v5A2 2 0 002 12.5h10a2 2 0 002-2v-5A2 2 0 0012 3.5H9.5V1c0-.552-.448-1-1-1S7.5.448 7.5 1v2.5h-1V1z"),
        (prs,     "Pull Requests", PURP, "M7.177 3.073L9.573.677A.25.25 0 0110 .854v4.792a.25.25 0 01-.427.177L7.177 3.427a.25.25 0 010-.354zM3.75 2.5a.75.75 0 100 1.5.75.75 0 000-1.5zm-2.25.75a2.25 2.25 0 113 2.122v5.256a2.251 2.251 0 11-1.5 0V5.372A2.25 2.25 0 011.5 3.25zM11 2.5h-1V4h1a1 1 0 011 1v5.628a2.251 2.251 0 101.5 0V5A2.5 2.5 0 0011 2.5zm1 10.25a.75.75 0 111.5 0 .75.75 0 01-1.5 0zM3.75 12a.75.75 0 100 1.5.75.75 0 000-1.5z"),
        (issues,  "Issues",        RED,  "M8 9.5a1.5 1.5 0 100-3 1.5 1.5 0 000 3z M8 0a8 8 0 100 16A8 8 0 008 0zM1.5 8a6.5 6.5 0 1113 0 6.5 6.5 0 01-13 0z"),
        (stars,   "Étoiles",       YELL, "M8 .25a.75.75 0 01.673.418l1.882 3.815 4.21.612a.75.75 0 01.416 1.279l-3.046 2.97.719 4.192a.75.75 0 01-1.088.791L8 12.347l-3.766 1.98a.75.75 0 01-1.088-.79l.72-4.194L.818 6.374a.75.75 0 01.416-1.28l4.21-.611L7.327.668A.75.75 0 018 .25z"),
        (n_repos, "Dépôts",        CYAN, "M2 2.5A2.5 2.5 0 014.5 0h8.75a.75.75 0 01.75.75v12.5a.75.75 0 01-.75.75h-2.5a.75.75 0 010-1.5h1.75v-2h-8a1 1 0 00-.714 1.7.75.75 0 01-1.072 1.05A2.495 2.495 0 012 11.5v-9zm10.5-1V9h-8c-.356 0-.694.074-1 .208V2.5a1 1 0 011-1h8z"),
        (follw,   "Abonnés",       GREE, "M5.5 3.5a2 2 0 100 4 2 2 0 000-4zM2 5.5a3.5 3.5 0 115.898 2.549 5.507 5.507 0 013.034 4.084.75.75 0 11-1.482.235 4.001 4.001 0 00-7.9 0 .75.75 0 01-1.482-.236A5.507 5.507 0 013.102 8.05 3.49 3.49 0 012 5.5z"),
    ]

    # Grid layout
    cells = []
    for i, (val, label, col, icon_path) in enumerate(STATS):
        col_idx = i % 2
        row_idx = i // 2
        x = 35 + col_idx * 200
        y = 100 + row_idx * 45
        
        cells.append(
            f'<g transform="translate({x},{y-15}) scale(1.3)"><path fill="{col}" d="{icon_path}"/></g>'
            f'<text x="{x+30}" y="{y-1}" font-size="18" font-weight="700" fill="{TEXT}">{val:,}</text>'
            f'<text x="{x+30}" y="{y+15}" font-size="12" fill="{DIM}">{label}</text>'
        )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="{BG}"/>
    <stop offset="100%" stop-color="{BG2}"/>
  </linearGradient>
</defs>
<style>text{{font-family:{FONT}}}</style>
<rect width="{W}" height="{H}" rx="10" fill="url(#bg)" stroke="{BORD}"/>
<text x="35" y="45" font-size="22" font-weight="700" fill="{BLUE}">{name}</text>
<text x="35" y="65" font-size="13" fill="{DIM}">@{USERNAME}</text>
<text x="385" y="65" font-size="13" fill="{DIM}" text-anchor="end">{total} contributions cette année</text>
<rect x="35" y="78" width="370" height="1" fill="{BORD}"/>
{''.join(cells)}
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
    # On limite à 5 langages pour avoir de l'espace et de la lisibilité
    langs   = sorted(lang_data.items(), key=lambda x: -x[1]["size"])[:5]
    total_top = sum(v["size"] for k, v in langs)
    
    W, H = 440, 240
    PAD = 35
    
    # Progress bar
    strip_w = W - 2 * PAD
    strip_x = PAD
    strip = [f'<rect x="{PAD}" y="70" width="{strip_w}" height="12" rx="6" fill="{BORD}"/>']
    
    for lang, info in langs:
        sw = strip_w * info["size"] / total_top
        strip.append(
            f'<rect x="{strip_x:.1f}" y="70" width="{max(sw,1):.1f}" height="12" fill="{info["color"]}"/>'
        )
        strip_x += sw
    strip.insert(0, f'<clipPath id="sc"><rect x="{PAD}" y="70" width="{strip_w}" height="12" rx="6"/></clipPath>')
    strip_body = [strip[0]] + [f'<g clip-path="url(#sc)">' + ''.join(strip[1:]) + '</g>']

    # List of languages
    rows = []
    for i, (lang, info) in enumerate(langs):
        pct = info["size"] / total_b * 100
        y = 105 + i * 26
        rows += [
            f'<circle cx="{PAD+6}" cy="{y-4}" r="6" fill="{info["color"]}"/>',
            f'<text x="{PAD+20}" y="{y+1}" font-size="14" font-weight="600" fill="{TEXT}">{esc(lang)}</text>',
            f'<text x="{W-PAD}" y="{y+1}" font-size="13" fill="{DIM}" text-anchor="end">{pct:.1f}%</text>',
        ]

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="{BG}"/>
    <stop offset="100%" stop-color="{BG2}"/>
  </linearGradient>
</defs>
<style>text{{font-family:{FONT}}}</style>
<rect width="{W}" height="{H}" rx="10" fill="url(#bg)" stroke="{BORD}"/>
<text x="{PAD}" y="45" font-size="18" font-weight="700" fill="{TEXT}">Langages les plus utilisés</text>
{''.join(strip_body)}
{''.join(rows)}
</svg>"""

# ── calendar.svg ───────────────────────────────────────────────────────────────
def calendar_svg(u):
    c      = u["contributionsCollection"]
    weeks  = c["contributionCalendar"]["weeks"]
    total  = c["contributionCalendar"]["totalContributions"]

    all_days = [d for w in weeks for d in w["contributionDays"]]
    max_c    = max((d["contributionCount"] for d in all_days), default=1) or 1

    # Plus gros pour être bien lisible sur un écran 1080p
    CELL, GAP = 14, 4
    PAD_L, PAD_T = 40, 70
    n_weeks = len(weeks)
    W = 890
    H = 220

    LVL = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
    MONTHS_FR = {1:"Jan", 2:"Fév", 3:"Mar", 4:"Avr", 5:"Mai", 6:"Juin", 
                 7:"Juil", 8:"Août", 9:"Sep", 10:"Oct", 11:"Nov", 12:"Déc"}

    cells = []
    month_labels = {}
    last_month = None
    
    for wi, week in enumerate(weeks):
        for day in week["contributionDays"]:
            dt  = datetime.fromisoformat(day["date"])
            di  = dt.weekday()
            cnt = day["contributionCount"]
            lvl = 0 if cnt == 0 else min(int(cnt / max_c * 3) + 1, 4)
            x = PAD_L + wi * (CELL + GAP)
            y = PAD_T + di * (CELL + GAP)
            cells.append(
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="3" fill="{LVL[lvl]}"/>'
            )
            
            if dt.month != last_month:
                month_labels[wi] = MONTHS_FR[dt.month]
                last_month = dt.month

    mlabels = [
        f'<text x="{PAD_L + wi*(CELL+GAP)}" y="{PAD_T-8}" font-size="12" fill="{TEXT}">{m}</text>'
        for wi, m in month_labels.items()
    ]
    dlabels = [
        f'<text x="{PAD_L-10}" y="{PAD_T + i*(CELL+GAP)+CELL-2}" font-size="11" fill="{DIM}" text-anchor="end">{d}</text>'
        for i, d in enumerate(["Lun","Mar","Mer","Jeu","Ven","Sam","Dim"])
    ]

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="{BG}"/>
    <stop offset="100%" stop-color="{BG2}"/>
  </linearGradient>
</defs>
<style>text{{font-family:{FONT}}}</style>
<rect width="{W}" height="{H}" rx="10" fill="url(#bg)" stroke="{BORD}"/>
<text x="{PAD_L}" y="35" font-size="20" font-weight="700" fill="{TEXT}">Contributions</text>
<text x="{PAD_L}" y="52" font-size="13" fill="{DIM}"><tspan fill="{GREE}" font-weight="700">{total}</tspan> contributions sur la dernière année</text>
{''.join(mlabels)}
{''.join(dlabels)}
{''.join(cells)}
</svg>"""

# ── activity.svg ───────────────────────────────────────────────────────────────
def activity_svg(u):
    c       = u["contributionsCollection"]
    all_d   = [d for w in c["contributionCalendar"]["weeks"] for d in w["contributionDays"]]
    days    = all_d[-30:]
    total   = sum(d["contributionCount"] for d in days)

    W, H = 890, 220
    PL, PR, PT, PB = 40, 40, 70, 45
    baw = W - PL - PR
    bah = H - PT - PB

    n = len(days)
    slot = baw / n
    gap  = slot * 0.25
    bw   = slot - gap
    max_c = max((d["contributionCount"] for d in days), default=1) or 1

    LVL = {0:"#161b22", 1:"#0e4429", 2:"#006d32", 3:"#26a641", 4:"#39d353"}
    def lvl(c):
        if c == 0: return 0
        r = c / max_c
        return 1 if r <= .25 else 2 if r <= .5 else 3 if r <= .75 else 4

    bars, labels = [], []
    for i, d in enumerate(days):
        cnt = d["contributionCount"]
        x   = PL + i * slot + gap / 2
        bh  = max((cnt / max_c) * bah, 4) if cnt else 4
        by  = PT + bah - bh
        bars.append(
            f'<rect x="{x:.1f}" y="{by:.1f}" width="{bw:.1f}" height="{bh:.1f}" '
            f'fill="{LVL[lvl(cnt)]}" rx="3"/>'
        )
        # Afficher 1 date sur 3 pour plus de clarté
        if i % 3 == 0 or i == n - 1:
            date_str = datetime.fromisoformat(d["date"]).strftime("%d %b")
            labels.append(
                f'<text x="{x+bw/2:.1f}" y="{PT+bah+20}" text-anchor="middle" '
                f'font-size="11" fill="{DIM}">{date_str}</text>'
            )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="{BG}"/>
    <stop offset="100%" stop-color="{BG2}"/>
  </linearGradient>
</defs>
<style>text{{font-family:{FONT}}}</style>
<rect width="{W}" height="{H}" rx="10" fill="url(#bg)" stroke="{BORD}"/>
<text x="{PL}" y="35" font-size="20" font-weight="700" fill="{TEXT}">Activité des 30 derniers jours</text>
<text x="{PL}" y="52" font-size="13" fill="{DIM}"><tspan fill="{BLUE}" font-weight="700">{total}</tspan> contributions le mois dernier</text>
<rect x="{PL}" y="{PT}" width="{baw}" height="{bah}" fill="#000000" opacity="0.1" rx="5"/>
<line x1="{PL}" y1="{PT+bah}" x2="{W-PR}" y2="{PT+bah}" stroke="{BORD}" stroke-width="2"/>
{''.join(bars)}
{''.join(labels)}
</svg>"""

# ── main ───────────────────────────────────────────────────────────────────────
def main():
    if not TOKEN:
        print("GH_TOKEN manquant", file=sys.stderr)
        sys.exit(1)

    print(f"📊 Génération du nouveau design pour @{USERNAME}...")
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
        print(f"  ✅ {path} généré.")

if __name__ == "__main__":
    main()
