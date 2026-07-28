#!/usr/bin/env python3
"""
Génère metrics/activity.svg à partir du calendrier de contributions GitHub
via l'API GraphQL (inclut les dépôts privés grâce à GH_TOKEN).
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta, timezone

TOKEN = os.environ.get("GH_TOKEN", "")
USERNAME = "ouzfeya7"

GRAPHQL_URL = "https://api.github.com/graphql"

QUERY = """
query($username: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $username) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      restrictedContributionsCount
    }
  }
}
"""


def fetch(from_dt, to_dt):
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
    }
    variables = {
        "username": USERNAME,
        "from": from_dt.isoformat(),
        "to": to_dt.isoformat(),
    }
    r = requests.post(
        GRAPHQL_URL,
        json={"query": QUERY, "variables": variables},
        headers=headers,
        timeout=30,
    )
    r.raise_for_status()
    data = r.json()
    if "errors" in data:
        print(f"GraphQL errors: {data['errors']}", file=sys.stderr)
        sys.exit(1)
    return data["data"]["user"]["contributionsCollection"]


def level(count, max_count):
    if count == 0:
        return 0
    ratio = count / max_count
    if ratio <= 0.25:
        return 1
    elif ratio <= 0.5:
        return 2
    elif ratio <= 0.75:
        return 3
    return 4


LEVEL_COLORS = {
    0: "#1e2030",
    1: "#0e4429",
    2: "#006d32",
    3: "#26a641",
    4: "#39d353",
}

BG = "#0d1117"
ACCENT = "#7aa2f7"
TEXT_DIM = "#565f89"
TEXT_BRIGHT = "#c0caf5"
CHART_BG = "#1a1b2e"


def build_svg(days, total, commits, prs, issues, restricted):
    W = 860
    H = 200
    PAD_L, PAD_R = 8, 8
    PAD_T, PAD_B = 44, 36
    bar_area_w = W - PAD_L - PAD_R
    bar_area_h = H - PAD_T - PAD_B

    n = len(days)
    bar_slot = bar_area_w / n
    gap = bar_slot * 0.25
    bw = bar_slot - gap

    max_c = max((d["contributionCount"] for d in days), default=1) or 1

    rects = []
    x_labels = []
    for i, d in enumerate(days):
        c = d["contributionCount"]
        x = PAD_L + i * bar_slot + gap / 2
        col = LEVEL_COLORS[level(c, max_c)]
        bh = max((c / max_c) * bar_area_h, 2) if c else 0
        by = PAD_T + bar_area_h - bh

        rects.append(
            f'<rect x="{x:.1f}" y="{by:.1f}" width="{bw:.1f}" '
            f'height="{max(bh,2):.1f}" fill="{col}" rx="2" opacity="0.95"/>'
        )
        if c > 0 and bh > 12:
            rects.append(
                f'<text x="{x+bw/2:.1f}" y="{by-3:.1f}" text-anchor="middle" '
                f'font-size="7" fill="{ACCENT}" opacity="0.7">{c}</text>'
            )

        if i % 5 == 0 or i == n - 1:
            date_label = d["date"][5:]
            label_y = PAD_T + bar_area_h + 18
            x_labels.append(
                f'<text x="{x+bw/2:.1f}" y="{label_y:.1f}" text-anchor="middle" '
                f'font-size="8.5" fill="{TEXT_DIM}">{date_label}</text>'
            )

    private_note = f" (+{restricted} privées)" if restricted > 0 else ""
    title = (
        f'Contributions — 30 derniers jours · '
        f'<tspan fill="{ACCENT}">{total}</tspan> au total{private_note}'
    )

    stat_items = [
        (commits, "Commits"),
        (prs,     "Pull Requests"),
        (issues,  "Issues"),
    ]
    stat_x = W - PAD_R - 2
    stat_svgs = []
    for val, lbl in reversed(stat_items):
        stat_svgs.append(
            f'<text x="{stat_x:.1f}" y="24" text-anchor="end" '
            f'font-size="11" fill="{TEXT_DIM}">'
            f'<tspan fill="{ACCENT}" font-weight="bold">{val}</tspan> {lbl}</text>'
        )
        stat_x -= 120

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <style>
    text {{ font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; }}
  </style>
  <rect width="{W}" height="{H}" rx="10" fill="{BG}" stroke="#30363d" stroke-width="1"/>
  <rect x="{PAD_L}" y="{PAD_T}" width="{bar_area_w}" height="{bar_area_h}" rx="4" fill="{CHART_BG}" opacity="0.5"/>
  <text x="10" y="24" font-size="12.5" fill="{TEXT_BRIGHT}" font-weight="600">{title}</text>
  {''.join(stat_svgs)}
  {''.join(rects)}
  {''.join(x_labels)}
</svg>"""
    return svg


def main():
    if not TOKEN:
        print("GH_TOKEN is not set", file=sys.stderr)
        sys.exit(1)

    now = datetime.now(timezone.utc)
    data = fetch(now - timedelta(days=30), now)

    calendar = data["contributionCalendar"]
    all_days = [
        day
        for week in calendar["weeks"]
        for day in week["contributionDays"]
    ]
    days = all_days[-30:]

    svg = build_svg(
        days=days,
        total=calendar["totalContributions"],
        commits=data["totalCommitContributions"],
        prs=data["totalPullRequestContributions"],
        issues=data["totalIssueContributions"],
        restricted=data["restrictedContributionsCount"],
    )

    os.makedirs("metrics", exist_ok=True)
    with open("metrics/activity.svg", "w", encoding="utf-8") as f:
        f.write(svg)

    print(
        f"✅ metrics/activity.svg généré "
        f"({calendar['totalContributions']} contributions, "
        f"{data['restrictedContributionsCount']} privées incluses)"
    )


if __name__ == "__main__":
    main()
