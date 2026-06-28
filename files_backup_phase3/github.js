/* =====================================================
   github.js  —  Phase 3
   Smart Career Recommendation System

   Responsibilities:
     • On page load: call GET /api/github/analysis to check
       for a previously stored result and render it.
     • Analyse button: POST /api/github/analyze with the
       entered username, show a loading spinner, then render.
     • Re-analyse button: pre-fill the username and trigger
       the same POST flow.
     • Clear button: DELETE /api/github/analysis, hide results.
     • Rendering helpers: score bars with colour coding,
       animated SVG ring, language colour palette, repo cards.
   ===================================================== */

document.addEventListener("DOMContentLoaded", function () {

    // ── Element references ────────────────────────────────────────────────────
    const usernameInput    = document.getElementById("githubUsername");
    const analyzeBtn       = document.getElementById("analyzeBtn");
    const analyzeBtnText   = document.getElementById("analyzeBtnText");
    const analyzeBtnSpinner= document.getElementById("analyzeBtnSpinner");
    const inputError       = document.getElementById("inputError");

    const cacheBar         = document.getElementById("cacheBar");
    const cacheBarText     = document.getElementById("cacheBarText");
    const reanalyzeBtn     = document.getElementById("reanalyzeBtn");
    const clearAnalysisBtn = document.getElementById("clearAnalysisBtn");

    const errorBanner      = document.getElementById("errorBanner");
    const resultsSection   = document.getElementById("resultsSection");

    // Profile hero
    const ghAvatar         = document.getElementById("ghAvatar");
    const ghName           = document.getElementById("ghName");
    const ghProfileLink    = document.getElementById("ghProfileLink");
    const ghBio            = document.getElementById("ghBio");
    const ghBadges         = document.getElementById("ghBadges");
    const ringFill         = document.getElementById("ringFill");
    const overallScoreDisplay = document.getElementById("overallScoreDisplay");

    // Stats
    const statRepos        = document.getElementById("statRepos");
    const statStars        = document.getElementById("statStars");
    const statForks        = document.getElementById("statForks");
    const statFollowers    = document.getElementById("statFollowers");
    const statFollowing    = document.getElementById("statFollowing");
    const statGists        = document.getElementById("statGists");

    // Dynamic containers
    const scoreList        = document.getElementById("scoreList");
    const langList         = document.getElementById("langList");
    const repoGrid         = document.getElementById("repoGrid");

    // ── GitHub language colour palette (top 60 languages) ────────────────────
    // Matches the official github-linguist colours as closely as possible.
    const LANG_COLORS = {
        "JavaScript":   "#f1e05a",
        "TypeScript":   "#3178c6",
        "Python":       "#3572A5",
        "Java":         "#b07219",
        "C":            "#555555",
        "C++":          "#f34b7d",
        "C#":           "#178600",
        "Go":           "#00ADD8",
        "Rust":         "#dea584",
        "Ruby":         "#701516",
        "PHP":          "#4F5D95",
        "Swift":        "#F05138",
        "Kotlin":       "#A97BFF",
        "Scala":        "#c22d40",
        "Shell":        "#89e051",
        "Bash":         "#89e051",
        "PowerShell":   "#012456",
        "HTML":         "#e34c26",
        "CSS":          "#563d7c",
        "SCSS":         "#c6538c",
        "Sass":         "#a53b70",
        "Vue":          "#41b883",
        "Svelte":       "#ff3e00",
        "Dart":         "#00B4AB",
        "Elixir":       "#6e4a7e",
        "Erlang":       "#B83998",
        "Haskell":      "#5e5086",
        "Lua":          "#000080",
        "R":            "#198CE7",
        "MATLAB":       "#e16737",
        "Julia":        "#a270ba",
        "Perl":         "#0298c3",
        "Groovy":       "#4298b8",
        "Clojure":      "#db5855",
        "CoffeeScript": "#244776",
        "Objective-C":  "#438eff",
        "OCaml":        "#3be133",
        "F#":           "#b845fc",
        "Nim":          "#ffc200",
        "Crystal":      "#000100",
        "Zig":          "#ec915c",
        "Assembly":     "#6E4C13",
        "Dockerfile":   "#384d54",
        "Makefile":     "#427819",
        "CMake":        "#DA3434",
        "Nix":          "#7e7eff",
        "Terraform":    "#7B42BC",
        "HCL":          "#844FBA",
        "YAML":         "#cb171e",
        "JSON":         "#292929",
        "XML":          "#0060ac",
        "Markdown":     "#083fa1",
        "Jupyter Notebook": "#DA5B0B",
        "Vim Script":   "#199f4b",
        "Emacs Lisp":   "#c065db",
        "TeX":          "#3D6117",
    };

    /** Return a deterministic pastel colour for languages not in the palette. */
    function langColor(name) {
        if (LANG_COLORS[name]) return LANG_COLORS[name];
        // Hash the name to a hue
        let hash = 0;
        for (let i = 0; i < name.length; i++) {
            hash = name.charCodeAt(i) + ((hash << 5) - hash);
        }
        const hue = Math.abs(hash) % 360;
        return `hsl(${hue}, 55%, 55%)`;
    }

    // ── Utility helpers ───────────────────────────────────────────────────────

    /** Escape user-supplied text before inserting as innerHTML. */
    function esc(str) {
        if (!str) return "";
        return String(str)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#39;");
    }

    /** Format large numbers with K / M suffixes. */
    function fmtNum(n) {
        if (n === null || n === undefined) return "—";
        if (n >= 1_000_000) return (n / 1_000_000).toFixed(1).replace(/\.0$/, "") + "M";
        if (n >= 1_000)     return (n / 1_000).toFixed(1).replace(/\.0$/, "")     + "K";
        return String(n);
    }

    /** Format an ISO timestamp as "Jan 15, 2024 at 09:31". */
    function fmtTimestamp(iso) {
        if (!iso) return "";
        try {
            const d = new Date(iso);
            return d.toLocaleString("en-US", {
                month: "short", day: "numeric", year: "numeric",
                hour: "2-digit", minute: "2-digit"
            });
        } catch {
            return iso;
        }
    }

    /** Format an ISO date string as "Jan 2021". */
    function fmtMonthYear(iso) {
        if (!iso) return "";
        try {
            const d = new Date(iso);
            return d.toLocaleString("en-US", { month: "short", year: "numeric" });
        } catch {
            return iso;
        }
    }

    /** Pick a CSS class for a score bar based on the 0-100 value. */
    function scoreBarClass(val) {
        if (val >= 70) return "gh-bar-great";
        if (val >= 45) return "gh-bar-good";
        if (val >= 20) return "gh-bar-mid";
        return "gh-bar-low";
    }

    // ── UI state helpers ──────────────────────────────────────────────────────

    function showError(msg) {
        errorBanner.textContent = msg;
        errorBanner.classList.remove("hidden");
    }

    function hideError() {
        errorBanner.classList.add("hidden");
        errorBanner.textContent = "";
    }

    function setInputError(msg) {
        inputError.textContent = msg;
    }

    function setLoading(isLoading) {
        analyzeBtn.disabled = isLoading;
        if (isLoading) {
            analyzeBtnText.textContent = "Analysing…";
            analyzeBtnSpinner.classList.remove("hidden");
        } else {
            analyzeBtnText.textContent = "Analyse";
            analyzeBtnSpinner.classList.add("hidden");
        }
    }

    // ── API helpers ───────────────────────────────────────────────────────────

    async function apiPost(url, body) {
        const res = await fetch(url, {
            method:  "POST",
            headers: { "Content-Type": "application/json" },
            body:    JSON.stringify(body),
        });
        return res.json();
    }

    async function apiGet(url) {
        const res = await fetch(url);
        return res.json();
    }

    async function apiDelete(url) {
        const res = await fetch(url, { method: "DELETE" });
        return res.json();
    }

    // ── Rendering ─────────────────────────────────────────────────────────────

    /**
     * Populate the entire results section from a data object that matches
     * what /api/github/analyze and /api/github/analysis both return.
     */
    function renderResults(d) {
        hideError();

        // ── Profile hero ──────────────────────────────────────────────────────
        ghAvatar.src = esc(d.github_avatar_url) || "https://github.com/ghost.png";
        ghAvatar.alt = `${esc(d.github_username)}'s avatar`;

        ghName.textContent = d.github_name || d.github_username;

        ghProfileLink.href        = esc(d.github_profile_url);
        ghProfileLink.textContent = `@${d.github_username}`;

        ghBio.textContent = d.github_bio || "";
        ghBio.style.display = d.github_bio ? "block" : "none";

        // Badges: location + account age
        const badges = [];
        if (d.github_location) {
            badges.push(`📍 ${esc(d.github_location)}`);
        }
        if (d.account_created_at) {
            badges.push(`📅 Joined ${fmtMonthYear(d.account_created_at)}`);
        }
        ghBadges.innerHTML = badges
            .map(b => `<span class="gh-badge">${b}</span>`)
            .join("");

        // ── Overall score ring (animated) ─────────────────────────────────────
        const overall = d.overall_score || 0;
        // Circumference = 2π × r = 2π × 50 ≈ 314.16
        const circumference = 314.16;
        const offset = circumference - (overall / 100) * circumference;

        overallScoreDisplay.textContent = "0";
        ringFill.style.strokeDashoffset = String(circumference); // start empty

        // Animate after a brief paint delay
        requestAnimationFrame(() => {
            setTimeout(() => {
                ringFill.style.strokeDashoffset = offset.toFixed(2);
                // Animate the number counter
                animateCounter(overallScoreDisplay, 0, Math.round(overall), 1200);
            }, 80);
        });

        // ── Stats row ─────────────────────────────────────────────────────────
        statRepos.textContent    = fmtNum(d.public_repos);
        statStars.textContent    = fmtNum(d.total_stars);
        statForks.textContent    = fmtNum(d.total_forks);
        statFollowers.textContent = fmtNum(d.followers);
        statFollowing.textContent = fmtNum(d.following);
        statGists.textContent    = fmtNum(d.public_gists);

        // ── Score breakdown ───────────────────────────────────────────────────
        const scores = [
            { label: "🏃 Activity Score",          value: d.activity_score,  desc: "Repos, gists, account age" },
            { label: "📁 Repository Score",         value: d.repo_score,      desc: "Stars, forks, quality signals" },
            { label: "🌐 Community Score",          value: d.community_score, desc: "Followers, following, presence" },
            { label: "🗂 Language Diversity",        value: d.lang_div_score,  desc: "Shannon entropy of language mix" },
        ];

        scoreList.innerHTML = scores.map(s => {
            const val      = s.value || 0;
            const barClass = scoreBarClass(val);
            return `
            <div class="gh-score-row">
                <div class="gh-score-meta">
                    <span class="gh-score-name" title="${esc(s.desc)}">${s.label}</span>
                    <span class="gh-score-value">${val.toFixed(1)}</span>
                </div>
                <div class="gh-score-bar-bg">
                    <div class="gh-score-bar-fill ${barClass}"
                         data-width="${val}"
                         style="width:0%"></div>
                </div>
            </div>`;
        }).join("");

        // Animate score bars after they're in the DOM
        requestAnimationFrame(() => {
            setTimeout(() => {
                scoreList.querySelectorAll(".gh-score-bar-fill").forEach(bar => {
                    bar.style.width = bar.dataset.width + "%";
                });
            }, 120);
        });

        // ── Language breakdown ────────────────────────────────────────────────
        const langData = d.language_table || [];
        if (langData.length === 0) {
            langList.innerHTML = `<div style="color:#aaa;font-size:13px;">No language data available.</div>`;
        } else {
            // Show top 10 languages
            langList.innerHTML = langData.slice(0, 10).map(row => {
                const color = langColor(row.language);
                const pct   = (row.percentage || 0).toFixed(1);
                return `
                <div class="gh-lang-row">
                    <span class="gh-lang-dot" style="background:${color}"></span>
                    <span class="gh-lang-name">${esc(row.language)}</span>
                    <div class="gh-lang-bar-wrap">
                        <div class="gh-lang-bar"
                             data-width="${Math.min(pct, 100)}"
                             style="width:0%;background:${color}"></div>
                    </div>
                    <span class="gh-lang-pct">${pct}%</span>
                </div>`;
            }).join("");

            // Animate language bars
            requestAnimationFrame(() => {
                setTimeout(() => {
                    langList.querySelectorAll(".gh-lang-bar").forEach(bar => {
                        bar.style.width = bar.dataset.width + "%";
                    });
                }, 150);
            });
        }

        // ── Top repositories ──────────────────────────────────────────────────
        const repos = d.top_repos || [];
        if (repos.length === 0) {
            repoGrid.innerHTML = `<div style="color:#aaa;font-size:13px;grid-column:1/-1;">No public repositories found.</div>`;
        } else {
            repoGrid.innerHTML = repos.map(r => repoCard(r)).join("");
        }

        // ── Show results ──────────────────────────────────────────────────────
        resultsSection.classList.remove("hidden");
        resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
    }

    /** Build the HTML for a single repo card. */
    function repoCard(r) {
        const color   = langColor(r.language || "");
        const topics  = (r.topics || []).slice(0, 4);
        const updated = fmtMonthYear(r.updated_at);

        return `
        <div class="gh-repo-card">
            <a class="gh-repo-name"
               href="${esc(r.url)}"
               target="_blank"
               rel="noopener">${esc(r.name)}</a>

            ${r.description
                ? `<div class="gh-repo-desc">${esc(r.description)}</div>`
                : ""}

            ${topics.length
                ? `<div class="gh-repo-topics">
                       ${topics.map(t => `<span class="gh-topic">${esc(t)}</span>`).join("")}
                   </div>`
                : ""}

            <div class="gh-repo-footer">
                ${r.language
                    ? `<span class="gh-repo-lang">
                           <span class="gh-repo-lang-dot" style="background:${color}"></span>
                           ${esc(r.language)}
                       </span>`
                    : ""}

                ${r.stars > 0
                    ? `<span class="gh-repo-stat">⭐ ${fmtNum(r.stars)}</span>`
                    : ""}

                ${r.forks > 0
                    ? `<span class="gh-repo-stat">🍴 ${fmtNum(r.forks)}</span>`
                    : ""}

                ${r.is_fork
                    ? `<span class="gh-fork-badge">fork</span>`
                    : ""}

                ${updated
                    ? `<span class="gh-repo-stat" style="margin-left:auto;color:#bbb">
                           ${updated}
                       </span>`
                    : ""}
            </div>
        </div>`;
    }

    /** Animate a numeric counter from start → end over durationMs. */
    function animateCounter(el, from, to, durationMs) {
        const startTime = performance.now();
        function step(now) {
            const elapsed  = now - startTime;
            const progress = Math.min(elapsed / durationMs, 1);
            // Ease out cubic
            const eased = 1 - Math.pow(1 - progress, 3);
            el.textContent = Math.round(from + (to - from) * eased);
            if (progress < 1) requestAnimationFrame(step);
        }
        requestAnimationFrame(step);
    }

    // ── Cache bar helpers ─────────────────────────────────────────────────────

    function showCacheBar(githubUsername, analyzedAt) {
        const timeStr = analyzedAt ? ` · Last analysed ${fmtTimestamp(analyzedAt)}` : "";
        cacheBarText.textContent = `Showing stored analysis for @${githubUsername}${timeStr}`;
        cacheBar.classList.remove("hidden");
    }

    function hideCacheBar() {
        cacheBar.classList.add("hidden");
    }

    function hideResults() {
        resultsSection.classList.add("hidden");
    }

    // ── On page load: fetch any stored analysis ───────────────────────────────

    (async function loadStoredAnalysis() {
        try {
            const result = await apiGet("/api/github/analysis");
            if (!result.success) return;
            if (!result.data) return;                 // no prior analysis

            const d = result.data;
            usernameInput.value = d.github_username;  // pre-fill input
            showCacheBar(d.github_username, d.analyzed_at);
            renderResults(d);
        } catch (err) {
            console.error("loadStoredAnalysis:", err);
        }
    })();

    // ── Analyse button ────────────────────────────────────────────────────────

    analyzeBtn.addEventListener("click", runAnalysis);

    usernameInput.addEventListener("keydown", function (e) {
        if (e.key === "Enter") runAnalysis();
    });

    usernameInput.addEventListener("input", function () {
        setInputError("");
    });

    async function runAnalysis() {
        const username = usernameInput.value.trim().replace(/^@/, "");

        setInputError("");
        hideError();

        if (!username) {
            setInputError("Please enter a GitHub username.");
            return;
        }

        // Basic format check: GitHub usernames are 1-39 chars,
        // only letters, numbers and single hyphens (not at start/end).
        if (!/^[a-zA-Z0-9]([a-zA-Z0-9-]{0,37}[a-zA-Z0-9])?$/.test(username) && username.length > 1) {
            setInputError("That doesn't look like a valid GitHub username.");
            return;
        }

        setLoading(true);
        hideCacheBar();
        hideResults();

        try {
            const result = await apiPost("/api/github/analyze", {
                github_username: username
            });

            if (result.success) {
                showCacheBar(result.data.github_username, null);
                renderResults(result.data);
            } else {
                showError("❌ " + (result.message || "Analysis failed. Please try again."));
            }
        } catch (err) {
            console.error("runAnalysis:", err);
            showError("❌ Network error. Check your connection and try again.");
        } finally {
            setLoading(false);
        }
    }

    // ── Re-analyse button ─────────────────────────────────────────────────────

    reanalyzeBtn.addEventListener("click", function () {
        // Username is already pre-filled from loadStoredAnalysis or the user
        hideCacheBar();
        hideResults();
        runAnalysis();
    });

    // ── Clear button ──────────────────────────────────────────────────────────

    clearAnalysisBtn.addEventListener("click", async function () {
        clearAnalysisBtn.disabled = true;
        clearAnalysisBtn.textContent = "Clearing…";

        try {
            const result = await apiDelete("/api/github/analysis");
            if (result.success) {
                hideCacheBar();
                hideResults();
                hideError();
                usernameInput.value = "";
                setInputError("");
            } else {
                showError(result.message || "Could not clear analysis.");
            }
        } catch (err) {
            console.error("clearAnalysis:", err);
            showError("Network error while clearing.");
        } finally {
            clearAnalysisBtn.disabled = false;
            clearAnalysisBtn.textContent = "✕ Clear";
        }
    });

}); // end DOMContentLoaded
