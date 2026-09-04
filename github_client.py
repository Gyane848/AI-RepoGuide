import requests
from config import GITHUB_TOKEN, GITHUB_API_BASE


def _headers():
    headers = {"Accept": "application/vnd.github+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return headers


def parse_repo_url(url):
    """Extract owner/repo from a GitHub URL."""
    url = url.strip().rstrip("/")
    parts = url.split("github.com/")[-1].split("/")
    if len(parts) < 2:
        raise ValueError("Invalid GitHub repo URL")
    return parts[0], parts[1]


def fetch_repo_data(repo_url):
    owner, repo = parse_repo_url(repo_url)
    base = f"{GITHUB_API_BASE}/repos/{owner}/{repo}"

    # 1. Repo metadata
    repo_resp = requests.get(base, headers=_headers())
    if repo_resp.status_code == 404:
        raise ValueError("Repo not found. Check the URL or make sure it's public.")
    repo_resp.raise_for_status()
    repo_info = repo_resp.json()

    # 2. README
    readme_text = ""
    readme_resp = requests.get(f"{base}/readme", headers={**_headers(), "Accept": "application/vnd.github.raw+json"})
    if readme_resp.status_code == 200:
        readme_text = readme_resp.text[:5000]  # cap length

    # 3. Languages
    lang_resp = requests.get(f"{base}/languages", headers=_headers())
    languages = list(lang_resp.json().keys()) if lang_resp.status_code == 200 else []

    # 4. Open issues (excluding pull requests)
    issues_resp = requests.get(
        f"{base}/issues",
        headers=_headers(),
        params={"state": "open", "per_page": 15}
    )
    issues = []
    if issues_resp.status_code == 200:
        for issue in issues_resp.json():
            if "pull_request" in issue:
                continue
            issues.append({
                "title": issue["title"],
                "number": issue["number"],
                "labels": [l["name"] for l in issue.get("labels", [])],
                "url": issue["html_url"],
            })

    # 5. CONTRIBUTING.md (optional)
    contributing_text = ""
    contrib_resp = requests.get(f"{base}/contents/CONTRIBUTING.md", headers=_headers())
    if contrib_resp.status_code == 200:
        import base64
        contributing_text = base64.b64decode(contrib_resp.json()["content"]).decode("utf-8", errors="ignore")[:2000]

    return {
        "name": repo_info.get("full_name"),
        "description": repo_info.get("description"),
        "stars": repo_info.get("stargazers_count"),
        "languages": languages,
        "readme": readme_text,
        "contributing": contributing_text,
        "issues": issues,
        "url": repo_info.get("html_url"),
    }