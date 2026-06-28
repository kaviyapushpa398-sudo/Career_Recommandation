"""
github_analyzer.py
-------------------
Phase 3: GitHub API integration for the Smart Career Recommendation System.

Responsibilities:
  - Fetch user profile, repositories, and per-repo language breakdowns
    from the GitHub REST API v3.
  - Compute five scores (activity, repo quality, community, language
    diversity, overall) all on a 0–100 scale.
  - Return a single structured dict that the Flask route can store in MySQL
    and pass straight to the frontend as JSON.

No Flask context is required here — this is a pure utility module.
"""

import os
import math
import json
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv

load_dotenv()

# ── Constants ─────────────────────────────────────────────────────────────────

GITHUB_API_BASE = "https://api.github.com"

# Max repos to fetch in a single analysis (GitHub API page size ≤ 100).
MAX_REPOS = 100

# Number of repos whose language breakdown we drill into.
# Language API calls are expensive (1 per repo), so cap at 30.
LANG_DRILL_LIMIT = 30

# Top-N repos to include in the stored summary JSON.
TOP_REPOS_SHOWN = 10

# Weights used in the overall score formula.
WEIGHT_ACTIVITY   = 0.30
WEIGHT_REPO       = 0.35
WEIGHT_COMMUNITY  = 0.20
WEIGHT_LANG_DIV   = 0.15


# ── Request helper ─────────────────────────────────────────────────────────────

def _headers() -> dict:
    """
    Build GitHub API request headers.
    A Personal Access Token (GITHUB_TOKEN env var) is optional but
    raises the rate limit from 60 to 5 000 requests/hour.
    """
    hdrs = {
        "Accept":     "application/vnd.github+json",
        "User-Agent": "SmartCareerSystem/3.0",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.getenv("GITHUB_TOKEN", "").strip()
    if token:
        hdrs["Authorization"] = f"Bearer {token}"
    return hdrs


def _get(url: str, params: dict | None = None) -> dict | list | None:
    """
    GET a GitHub API URL.  Returns parsed JSON or None on any error.
    Surfaces rate-limit information as a special dict when hit.
    """
    try:
        resp = requests.get(url, headers=_headers(), params=params, timeout=12)
        if resp.status_code == 404:
            return {"_error": "not_found"}
        if resp.status_code == 403:
            reset_ts = resp.headers.get("X-RateLimit-Reset", "")
            return {"_error": "rate_limited", "_reset": reset_ts}
        if resp.status_code != 200:
            return {"_error": f"http_{resp.status_code}"}
        return resp.json()
    except requests.RequestException as exc:
        return {"_error": str(exc)}


# ── Score calculators ──────────────────────────────────────────────────────────

def _clamp(val: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, val))


def _log_score(value: int, scale: int) -> float:
    """Logarithmic score that approaches 100 asymptotically."""
    if value <= 0:
        return 0.0
    return _clamp(math.log1p(value) / math.log1p(scale) * 100)


def compute_activity_score(repos: list, user: dict) -> float:
    """
    Activity score (0-100).

    Signals:
      - Number of public repos   (log scale, reference = 50)
      - Number of public gists   (log scale, reference = 20)
      - Account age in days      (log scale, reference = 1825 = 5 yrs)
      - Has a bio                (+5 bonus)
      - Has a website/blog       (+5 bonus)
    """
    repo_s  = _log_score(user.get("public_repos", 0),  50)
    gist_s  = _log_score(user.get("public_gists", 0),  20)

    created = user.get("created_at", "")
    age_days = 0
    if created:
        try:
            dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
            age_days = (datetime.now(timezone.utc) - dt).days
        except ValueError:
            pass
    age_s = _log_score(age_days, 1825)

    bonus = 0
    if user.get("bio"):  bonus += 5
    if user.get("blog"): bonus += 5

    raw = repo_s * 0.5 + gist_s * 0.15 + age_s * 0.35 + bonus
    return _clamp(raw)


def compute_repo_score(repos: list) -> float:
    """
    Repository quality score (0-100).

    Signals:
      - Total stars across all repos    (log, ref = 500)
      - Total forks across all repos    (log, ref = 200)
      - Average repo description rate   (% repos that have a description)
      - Average repo topic count        (topics = search keywords)
      - Fraction of repos not forked    (original work ratio)
    """
    if not repos:
        return 0.0

    total_stars = sum(r.get("stargazers_count", 0) for r in repos)
    total_forks = sum(r.get("forks_count", 0) for r in repos)

    star_s = _log_score(total_stars, 500)
    fork_s = _log_score(total_forks, 200)

    with_desc  = sum(1 for r in repos if r.get("description"))
    with_topics = sum(len(r.get("topics", [])) for r in repos)
    non_forked  = sum(1 for r in repos if not r.get("fork"))

    desc_rate  = (with_desc  / len(repos)) * 100
    topic_s    = _log_score(with_topics, len(repos) * 5)
    orig_ratio = (non_forked / len(repos)) * 100

    raw = star_s * 0.40 + fork_s * 0.20 + desc_rate * 0.15 + topic_s * 0.10 + orig_ratio * 0.15
    return _clamp(raw)


def compute_community_score(user: dict) -> float:
    """
    Community / social score (0-100).

    Signals:
      - Followers    (log, ref = 500)
      - Following    (log, ref = 200)
      - Has location (+5 bonus)
      - Has email    (+5 bonus)
    """
    follower_s  = _log_score(user.get("followers", 0),  500)
    following_s = _log_score(user.get("following", 0),  200)

    bonus = 0
    if user.get("location"): bonus += 5
    if user.get("email"):    bonus += 5

    raw = follower_s * 0.65 + following_s * 0.25 + bonus
    return _clamp(raw)


def compute_language_diversity_score(languages: dict) -> float:
    """
    Language diversity score (0-100) using Shannon entropy.

    A developer who is fluent in many languages scores higher.
    Reference: entropy of a perfectly uniform 10-language distribution.
    """
    total = sum(languages.values())
    if total == 0 or len(languages) == 0:
        return 0.0

    probs   = [v / total for v in languages.values()]
    entropy = -sum(p * math.log2(p) for p in probs if p > 0)
    # Normalise against log2(10) ≈ 3.32 (max entropy for 10 languages)
    max_entropy = math.log2(min(len(languages), 10))
    if max_entropy == 0:
        return 0.0

    # Also factor in raw language count (more languages is better up to 10)
    count_bonus = min(len(languages), 10) / 10 * 20
    diversity   = (entropy / max_entropy) * 80 + count_bonus
    return _clamp(diversity)


# ── Language aggregation ───────────────────────────────────────────────────────

def _fetch_repo_languages(repos: list) -> dict:
    """
    For each repo (up to LANG_DRILL_LIMIT), hit the languages endpoint
    and accumulate byte counts.  Returns {language: total_bytes}.
    """
    aggregated: dict[str, int] = {}
    # Sort by stars descending so most relevant repos are drilled first
    sorted_repos = sorted(repos, key=lambda r: r.get("stargazers_count", 0), reverse=True)

    for repo in sorted_repos[:LANG_DRILL_LIMIT]:
        url  = repo.get("languages_url", "")
        if not url:
            continue
        lang_data = _get(url)
        if not isinstance(lang_data, dict) or "_error" in lang_data:
            continue
        for lang, count in lang_data.items():
            aggregated[lang] = aggregated.get(lang, 0) + count

    return aggregated


def _language_repo_counts(repos: list) -> dict:
    """Returns {language: number_of_repos_using_it} from repo.language field."""
    counts: dict[str, int] = {}
    for repo in repos:
        lang = repo.get("language")
        if lang:
            counts[lang] = counts.get(lang, 0) + 1
    return counts


# ── Top-repos summary ──────────────────────────────────────────────────────────

def _top_repos_summary(repos: list) -> list:
    """
    Return the top N repos sorted by stars, with a compact summary dict
    suitable for JSON storage and frontend rendering.
    """
    sorted_repos = sorted(repos, key=lambda r: r.get("stargazers_count", 0), reverse=True)
    out = []
    for r in sorted_repos[:TOP_REPOS_SHOWN]:
        out.append({
            "name":        r.get("name", ""),
            "description": r.get("description") or "",
            "language":    r.get("language") or "",
            "stars":       r.get("stargazers_count", 0),
            "forks":       r.get("forks_count", 0),
            "watchers":    r.get("watchers_count", 0),
            "topics":      r.get("topics", []),
            "is_fork":     r.get("fork", False),
            "url":         r.get("html_url", ""),
            "updated_at":  r.get("updated_at", ""),
        })
    return out


# ── Main public function ───────────────────────────────────────────────────────

def analyze_github_user(github_username: str) -> dict:
    """
    Full pipeline: fetch → analyse → score → return result dict.

    Returns a dict with either:
      { "success": True,  "data": { ... } }
    or
      { "success": False, "message": "..." }

    The caller (Flask route) is responsible for persisting to MySQL.
    """
    username = github_username.strip().lstrip("@")
    if not username:
        return {"success": False, "message": "GitHub username cannot be empty."}

    # ── 1. Fetch user profile ──────────────────────────────────────────────────
    user = _get(f"{GITHUB_API_BASE}/users/{username}")
    if not isinstance(user, dict):
        return {"success": False, "message": "Unexpected response from GitHub API."}
    if "_error" in user:
        if user["_error"] == "not_found":
            return {"success": False, "message": f"GitHub user '{username}' not found."}
        if user["_error"] == "rate_limited":
            return {"success": False, "message": "GitHub API rate limit hit. Add a GITHUB_TOKEN in .env or wait an hour."}
        return {"success": False, "message": f"GitHub API error: {user['_error']}"}

    # ── 2. Fetch repositories (up to MAX_REPOS) ────────────────────────────────
    repos_raw = _get(
        f"{GITHUB_API_BASE}/users/{username}/repos",
        params={"per_page": MAX_REPOS, "sort": "updated", "type": "owner"}
    )
    if not isinstance(repos_raw, list):
        repos_raw = []

    # ── 3. Fetch language byte-counts (drill per repo) ─────────────────────────
    lang_bytes = _fetch_repo_languages(repos_raw)

    # ── 4. Build language percentage table ─────────────────────────────────────
    total_bytes = sum(lang_bytes.values()) or 1
    lang_repo_counts = _language_repo_counts(repos_raw)

    language_table = []
    for lang, bcount in sorted(lang_bytes.items(), key=lambda x: x[1], reverse=True):
        language_table.append({
            "language":   lang,
            "bytes":      bcount,
            "repo_count": lang_repo_counts.get(lang, 0),
            "percentage": round(bcount / total_bytes * 100, 2),
        })

    top_languages = [lt["language"] for lt in language_table[:10]]

    # ── 5. Compute scores ──────────────────────────────────────────────────────
    activity_score   = compute_activity_score(repos_raw, user)
    repo_score       = compute_repo_score(repos_raw)
    community_score  = compute_community_score(user)
    lang_div_score   = compute_language_diversity_score(lang_bytes)

    overall_score = (
        activity_score  * WEIGHT_ACTIVITY  +
        repo_score      * WEIGHT_REPO      +
        community_score * WEIGHT_COMMUNITY +
        lang_div_score  * WEIGHT_LANG_DIV
    )
    overall_score = _clamp(overall_score)

    # ── 6. Aggregate totals ────────────────────────────────────────────────────
    total_stars    = sum(r.get("stargazers_count", 0) for r in repos_raw)
    total_forks    = sum(r.get("forks_count",     0) for r in repos_raw)
    total_watchers = sum(r.get("watchers_count",  0) for r in repos_raw)

    # ── 7. Pack and return ─────────────────────────────────────────────────────
    return {
        "success": True,
        "data": {
            # GitHub identity
            "github_username":    user.get("login", username),
            "github_name":        user.get("name") or "",
            "github_bio":         user.get("bio") or "",
            "github_avatar_url":  user.get("avatar_url") or "",
            "github_profile_url": user.get("html_url") or f"https://github.com/{username}",
            "github_location":    user.get("location") or "",
            "account_created_at": user.get("created_at") or "",

            # Repo stats
            "public_repos":    user.get("public_repos", 0),
            "total_stars":     total_stars,
            "total_forks":     total_forks,
            "total_watchers":  total_watchers,

            # Social stats
            "followers":    user.get("followers", 0),
            "following":    user.get("following", 0),
            "public_gists": user.get("public_gists", 0),

            # Scores (rounded to 2dp for display)
            "activity_score":   round(activity_score,  2),
            "repo_score":       round(repo_score,       2),
            "community_score":  round(community_score,  2),
            "lang_div_score":   round(lang_div_score,   2),
            "overall_score":    round(overall_score,    2),

            # Languages
            "top_languages":  top_languages,
            "language_table": language_table,   # full breakdown

            # Repo summaries
            "top_repos": _top_repos_summary(repos_raw),
        }
    }
