#!/usr/bin/env python3
"""Fetch the numbers the profile cards need and write data/profile.json.

Standard library only. Token lookup: ORG_TOKEN (a PAT, counts private work), then
GITHUB_TOKEN (CI built-in, public data only), then `gh auth token` for local runs.

Env: LOGIN (default NovaIsCoding), ORGS (comma list, default the four below).
"""
import datetime
import json
import os
import subprocess
import urllib.request

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "data", "profile.json")
LOGIN = os.environ.get("LOGIN", "NovaIsCoding")
ORGS = [o.strip() for o in os.environ.get("ORGS", "Census-Pro,Attendance-Pro,BhutanApp,LuckyPem").split(",") if o.strip()]


def token():
    t = os.environ.get("ORG_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if t:
        return t
    return subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, check=True).stdout.strip()


TOKEN = token()


def gql(query, variables):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json", "User-Agent": "profile-cards"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        out = json.load(r)
    if out.get("errors") and not out.get("data"):
        raise SystemExit(f"GitHub API error: {out['errors']}")
    return out["data"]


REPO_FIELDS = "name nameWithOwner description url stargazerCount primaryLanguage{name} isPrivate"
user = gql(
    """query($login:String!){
      user(login:$login){
        contributionsCollection{
          totalCommitContributions totalPullRequestContributions totalIssueContributions
          restrictedContributionsCount
          contributionCalendar{totalContributions weeks{contributionDays{date contributionCount contributionLevel}}}
        }
        pinnedItems(first:6, types:REPOSITORY){nodes{... on Repository{%s}}}
        repositories(first:8, privacy:PUBLIC, ownerAffiliations:OWNER, isFork:false,
                     orderBy:{field:PUSHED_AT, direction:DESC}){nodes{%s}}
      }
    }""" % (REPO_FIELDS, REPO_FIELDS),
    {"login": LOGIN},
)["user"]

cc = user["contributionsCollection"]
days = [d for w in cc["contributionCalendar"]["weeks"] for d in w["contributionDays"]]

# streak: walk back from today; today may still be empty without breaking the streak
today = datetime.date.today().isoformat()
counts = {d["date"]: d["contributionCount"] for d in days}
streak = 0
for d in reversed(days):
    if d["date"] > today:
        continue
    if d["contributionCount"] > 0:
        streak += 1
    elif d["date"] == today:
        continue
    else:
        break

months = {}
for d in days:
    months[d["date"][:7]] = months.get(d["date"][:7], 0) + d["contributionCount"]
months = [{"month": k, "count": v} for k, v in sorted(months.items())][-12:]

repos = [r for r in (user["pinnedItems"]["nodes"] or []) if r and not r.get("isPrivate")]
if len(repos) < 3:
    seen = {r["nameWithOwner"] for r in repos}
    repos += [r for r in user["repositories"]["nodes"] if r["nameWithOwner"] not in seen]
repos = [r for r in repos if r["name"].lower() != LOGIN.lower()][:3]  # not the profile repo itself

org_repos = org_stars = 0
for o in ORGS:
    try:
        d = gql(
            "query($o:String!){organization(login:$o){repositories(first:100){totalCount nodes{stargazerCount}}}}",
            {"o": o},
        )["organization"]["repositories"]
        org_repos += d["totalCount"]
        org_stars += sum(n["stargazerCount"] for n in d["nodes"])
    except Exception as e:  # noqa: BLE001 - keep going if one org is unreadable with this token
        print(f"warning: could not read org {o}: {e}")

data = {
    "login": LOGIN,
    "updated": today,
    "total": cc["contributionCalendar"]["totalContributions"],
    # private-repo commits are "restricted": counted by GitHub but not attributable
    "commits": cc["totalCommitContributions"] + cc["restrictedContributionsCount"],
    "prs": cc["totalPullRequestContributions"],
    "issues": cc["totalIssueContributions"],
    "streak": streak,
    "active_days": sum(1 for d in days if d["contributionCount"] > 0),
    "total_days": len([d for d in days if d["date"] <= today]),
    "busiest": max(counts.values() or [0]),
    "months": months,
    "weeks": [[{"date": d["date"], "n": d["contributionCount"], "level": d["contributionLevel"]} for d in w["contributionDays"]]
              for w in cc["contributionCalendar"]["weeks"]],
    "orgs": ORGS,
    "org_repos": org_repos,
    "org_stars": org_stars,
    "repos": [{"name": r["name"], "url": r["url"], "desc": r["description"] or "",
               "lang": (r["primaryLanguage"] or {}).get("name", ""), "stars": r["stargazerCount"]} for r in repos],
}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w") as f:
    json.dump(data, f, indent=1)
print(f"wrote data/profile.json: {data['total']} contributions, streak {streak}, {org_repos} org repos, {len(repos)} repos")
