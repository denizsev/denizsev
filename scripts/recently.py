"""Rewrite the RECENTLY block in README.md with the latest commits on public repos."""
import json, os, re, urllib.request

USER = "denizsev"
SKIP = {USER, f"{USER}.github.io", "basic-shopping-card"}  # profile repos and tutorial copies
TOKEN = os.environ.get("GITHUB_TOKEN", "")

def shorten(text, limit=70):
    """Cut long commit titles at a word boundary instead of mid-word."""
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(" ", 1)[0].rstrip(",;:") + "…"


def get(url):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json", **({"Authorization": f"Bearer {TOKEN}"} if TOKEN else {})})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)

repos = [r for r in get(f"https://api.github.com/users/{USER}/repos?per_page=100&sort=pushed")
         if not r["private"] and not r["archived"] and not r["fork"] and r["name"] not in SKIP]
items = []
for r in repos[:6]:
    commits = get(f"https://api.github.com/repos/{USER}/{r['name']}/commits?per_page=1")
    if not commits:
        continue
    c = commits[0]
    msg = shorten(c["commit"]["message"].splitlines()[0])
    day = c["commit"]["author"]["date"][:10]
    items.append(f"- **[{r['name']}]({r['html_url']})**: [{msg}]({c['html_url']}) · {day}")
block = "\n".join(items[:5]) or "- nothing public this week"
path = "README.md"
text = open(path, encoding="utf-8").read()
text = re.sub(r"(<!-- RECENTLY:START -->).*?(<!-- RECENTLY:END -->)", lambda m: m.group(1) + "\n" + block + "\n" + m.group(2), text, flags=re.S)
open(path, "w", encoding="utf-8").write(text)
