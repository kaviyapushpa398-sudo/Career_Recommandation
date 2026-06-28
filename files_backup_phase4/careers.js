/* =====================================================
   careers.js  —  Phase 4
   Smart Career Recommendation System

   Responsibilities
   ─────────────────
   • On page load: GET /api/careers/recommendations
     → if stored results exist, render them immediately.
   • Generate button: POST /api/careers/generate
     → show spinner, render results on success.
   • Re-run button: re-triggers POST flow.
   • Clear button:  DELETE /api/careers/recommendations.
   • Rankings sidebar: clicking a career switches the
     detail panel to that career's full breakdown.
   • Rendering: animated ring, score bars with colour
     coding, matched/missing skill tags, roadmap
     timeline, cert/course suggestions, skill-gap chips.
   ===================================================== */

document.addEventListener("DOMContentLoaded", function () {

    // ── Element refs ──────────────────────────────────────────────────────────
    const generateBtn        = document.getElementById("generateBtn");
    const generateBtnText    = document.getElementById("generateBtnText");
    const generateBtnSpinner = document.getElementById("generateBtnSpinner");

    const infoBar            = document.getElementById("infoBar");
    const infoBarText        = document.getElementById("infoBarText");
    const rerunBtn           = document.getElementById("rerunBtn");
    const clearBtn           = document.getElementById("clearBtn");

    const errorBanner        = document.getElementById("errorBanner");
    const warnBanner         = document.getElementById("warnBanner");
    const resultsSection     = document.getElementById("resultsSection");

    // Hero
    const heroBadge          = document.getElementById("heroBadge");
    const heroTitle          = document.getElementById("heroTitle");
    const heroCategory       = document.getElementById("heroCategory");
    const heroMatchPct       = document.getElementById("heroMatchPct");
    const heroRingFill       = document.getElementById("heroRingFill");
    const heroRingValue      = document.getElementById("heroRingValue");

    // Detail panel
    const rankingsPanel      = document.getElementById("rankingsPanel");
    const scoreGrid          = document.getElementById("scoreGrid");
    const scoreBars          = document.getElementById("scoreBars");
    const matchedSkillsTags  = document.getElementById("matchedSkillsTags");
    const missingSkillsTags  = document.getElementById("missingSkillsTags");
    const roadmapList        = document.getElementById("roadmapList");
    const certSuggestions    = document.getElementById("certSuggestions");
    const courseSuggestions  = document.getElementById("courseSuggestions");

    // Skill gaps
    const skillGapsTags      = document.getElementById("skillGapsTags");

    // ── State ─────────────────────────────────────────────────────────────────
    /** Full recommendations array — populated on load or generate. */
    let allRecommendations   = [];
    /** Index of the recommendation currently shown in the detail panel. */
    let selectedIndex        = 0;

    // ── Career emoji map ──────────────────────────────────────────────────────
    const CAREER_EMOJI = {
        "Software Developer":    "💻",
        "Full Stack Developer":  "🌐",
        "Frontend Developer":    "🎨",
        "Backend Developer":     "⚙️",
        "AI Engineer":           "🤖",
        "Data Analyst":          "📊",
        "Cloud Engineer":        "☁️",
        "Cybersecurity Analyst": "🔐",
    };

    function careerEmoji(title) {
        return CAREER_EMOJI[title] || "🎯";
    }

    // ── Utility helpers ───────────────────────────────────────────────────────

    function esc(str) {
        if (!str) return "";
        return String(str)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#39;");
    }

    function fmtPct(val) {
        return (val == null ? 0 : Math.round(val)) + "%";
    }

    function fmtScore(val) {
        return val == null ? "0.0" : Number(val).toFixed(1);
    }

    /** Return a score-bar CSS class based on 0-100 value. */
    function barClass(val) {
        if (val >= 70) return "cr-bar-great";
        if (val >= 45) return "cr-bar-good";
        if (val >= 20) return "cr-bar-mid";
        return "cr-bar-low";
    }

    /** Format ISO timestamp as "Jun 15, 2025 at 09:31". */
    function fmtTimestamp(iso) {
        if (!iso) return "";
        try {
            return new Date(iso).toLocaleString("en-US", {
                month: "short", day: "numeric", year: "numeric",
                hour: "2-digit", minute: "2-digit"
            });
        } catch { return iso; }
    }

    /** Animate a span's text from 0 to `to` over `durationMs`. */
    function animateCounter(el, to, durationMs = 1000) {
        const start = performance.now();
        function step(now) {
            const p = Math.min((now - start) / durationMs, 1);
            const eased = 1 - Math.pow(1 - p, 3);   // ease-out cubic
            el.textContent = Math.round(to * eased);
            if (p < 1) requestAnimationFrame(step);
        }
        requestAnimationFrame(step);
    }

    // ── UI state ──────────────────────────────────────────────────────────────

    function showError(msg) {
        errorBanner.textContent = msg;
        errorBanner.classList.remove("hidden");
    }
    function hideError() {
        errorBanner.textContent = "";
        errorBanner.classList.add("hidden");
    }

    function showWarn(msg) {
        warnBanner.textContent = msg;
        warnBanner.classList.remove("hidden");
    }
    function hideWarn() {
        warnBanner.textContent = "";
        warnBanner.classList.add("hidden");
    }

    function setGenerating(on) {
        generateBtn.disabled = on;
        generateBtnText.textContent = on ? "Generating…" : "✨ Generate";
        generateBtnSpinner.classList.toggle("hidden", !on);
    }

    function showInfoBar(text) {
        infoBarText.textContent = text;
        infoBar.classList.remove("hidden");
    }
    function hideInfoBar() { infoBar.classList.add("hidden"); }

    function showResults() { resultsSection.classList.remove("hidden"); }
    function hideResults() { resultsSection.classList.add("hidden"); }

    // ── API helpers ───────────────────────────────────────────────────────────

    async function apiPost(url) {
        const res = await fetch(url, {
            method:  "POST",
            headers: { "Content-Type": "application/json" },
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

    // ── On page load: fetch any stored recommendations ────────────────────────

    (async function loadStoredRecommendations() {
        try {
            const result = await apiGet("/api/careers/recommendations");
            if (!result.success || !result.data) return;

            const d = result.data;
            allRecommendations = d.recommendations || [];

            if (allRecommendations.length === 0) return;

            const ts = d.generated_at ? fmtTimestamp(d.generated_at) : "";
            showInfoBar(`Showing stored recommendations${ts ? " · Generated " + ts : ""}`);

            renderAll(allRecommendations, d.skill_gaps || []);

        } catch (err) {
            console.error("loadStoredRecommendations:", err);
        }
    })();

    // ── Generate button ───────────────────────────────────────────────────────

    generateBtn.addEventListener("click", runGenerate);
    rerunBtn.addEventListener("click",    runGenerate);

    async function runGenerate() {
        hideError();
        hideWarn();
        hideInfoBar();
        hideResults();
        setGenerating(true);

        try {
            const result = await apiPost("/api/careers/generate");

            if (result.success) {
                allRecommendations = result.recommendations || [];
                const gaps         = result.skill_gaps      || [];

                showInfoBar("Recommendations generated just now.");
                renderAll(allRecommendations, gaps);

            } else {
                // Special case: missing profile data
                if (result.message && result.message.includes("skills or interests")) {
                    showWarn("⚠️ " + result.message);
                } else {
                    showError("❌ " + (result.message || "Could not generate recommendations."));
                }
            }
        } catch (err) {
            console.error("runGenerate:", err);
            showError("❌ Network error. Please check your connection and try again.");
        } finally {
            setGenerating(false);
        }
    }

    // ── Clear button ──────────────────────────────────────────────────────────

    clearBtn.addEventListener("click", async function () {
        clearBtn.disabled = true;
        clearBtn.textContent = "Clearing…";

        try {
            const result = await apiDelete("/api/careers/recommendations");
            if (result.success) {
                allRecommendations = [];
                hideInfoBar();
                hideResults();
                hideError();
                hideWarn();
            } else {
                showError(result.message || "Could not clear recommendations.");
            }
        } catch (err) {
            showError("Network error while clearing.");
        } finally {
            clearBtn.disabled = false;
            clearBtn.textContent = "✕ Clear";
        }
    });

    // ── Master render function ────────────────────────────────────────────────

    /**
     * Renders the hero card, rankings sidebar, detail panel, and skill-gap
     * section from the full recommendations + gaps arrays.
     */
    function renderAll(recommendations, gaps) {
        if (!recommendations || recommendations.length === 0) return;

        selectedIndex = 0;

        // Hero = rank #1
        renderHero(recommendations[0]);

        // Rankings sidebar
        renderRankings(recommendations);

        // Detail panel = rank #1 initially
        renderDetail(recommendations[0]);

        // Skill gaps
        renderSkillGaps(gaps);

        showResults();
        resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
    }

    // ── Hero card ─────────────────────────────────────────────────────────────

    function renderHero(rec) {
        const pct = Math.round(rec.match_percentage || 0);

        heroBadge.textContent       = careerEmoji(rec.career_title);
        heroTitle.textContent       = rec.career_title;
        heroCategory.textContent    = rec.career_category || "";
        heroMatchPct.textContent    = fmtPct(pct);

        // Animated ring  (circumference ≈ 2π × 46 ≈ 289)
        const circumference = 289;
        const offset        = circumference - (pct / 100) * circumference;

        heroRingValue.textContent        = "0";
        heroRingFill.style.strokeDashoffset = String(circumference);

        requestAnimationFrame(() => {
            setTimeout(() => {
                heroRingFill.style.strokeDashoffset = offset.toFixed(2);
                animateCounter(heroRingValue, pct, 1300);
            }, 80);
        });
    }

    // ── Rankings sidebar ──────────────────────────────────────────────────────

    function renderRankings(recommendations) {
        // Keep the header that's already in the DOM, inject rank items after it
        const header = rankingsPanel.querySelector(".cr-rankings-header");
        // Remove old items (everything after the header)
        while (rankingsPanel.children.length > 1) {
            rankingsPanel.removeChild(rankingsPanel.lastChild);
        }

        recommendations.forEach((rec, idx) => {
            const item = document.createElement("div");
            item.className = "cr-rank-item" + (idx === 0 ? " active" : "");
            item.dataset.index = String(idx);
            item.innerHTML = `
                <div class="cr-rank-num">${rec.rank_position}</div>
                <div class="cr-rank-info">
                    <div class="cr-rank-title">${esc(rec.career_title)}</div>
                    <div class="cr-rank-category">${esc(rec.career_category || "")}</div>
                </div>
                <div class="cr-rank-pct">${Math.round(rec.match_percentage)}%</div>`;

            item.addEventListener("click", function () {
                selectedIndex = idx;
                // Update active state
                rankingsPanel.querySelectorAll(".cr-rank-item")
                    .forEach(el => el.classList.remove("active"));
                item.classList.add("active");
                renderDetail(allRecommendations[idx]);
            });

            rankingsPanel.appendChild(item);
        });
    }

    // ── Detail panel ──────────────────────────────────────────────────────────

    function renderDetail(rec) {
        renderScoreBreakdown(rec);
        renderSkillTags(rec);
        renderRoadmap(rec);
        renderSuggestions(rec);
    }

    // Score grid + bars
    function renderScoreBreakdown(rec) {
        const boxes = [
            { label: "Match",    value: fmtScore(rec.match_percentage) + "%" },
            { label: "Skills",   value: fmtScore(rec.skill_score) },
            { label: "Interest", value: fmtScore(rec.interest_score) },
            { label: "Certs",    value: fmtScore(rec.cert_score) },
            { label: "Projects", value: fmtScore(rec.project_score) },
            { label: "GitHub",   value: fmtScore(rec.github_score) },
        ];

        scoreGrid.innerHTML = boxes.map(b => `
            <div class="cr-score-box">
                <div class="cr-score-box-value">${esc(b.value)}</div>
                <div class="cr-score-box-label">${esc(b.label)}</div>
            </div>`).join("");

        const bars = [
            { name: "Skill Match",         value: rec.skill_score },
            { name: "Interest Alignment",  value: rec.interest_score },
            { name: "Certifications",      value: rec.cert_score },
            { name: "Project Experience",  value: rec.project_score },
            { name: "GitHub Activity",     value: rec.github_score },
        ];

        scoreBars.innerHTML = bars.map(b => {
            const val = b.value || 0;
            return `
            <div class="cr-score-row">
                <div class="cr-score-meta">
                    <span class="cr-score-name">${esc(b.name)}</span>
                    <span class="cr-score-val">${fmtScore(val)}</span>
                </div>
                <div class="cr-score-bar-bg">
                    <div class="cr-score-bar-fill ${barClass(val)}"
                         data-width="${Math.min(val, 100)}"
                         style="width:0%"></div>
                </div>
            </div>`;
        }).join("");

        // Animate bars after paint
        requestAnimationFrame(() => {
            setTimeout(() => {
                scoreBars.querySelectorAll(".cr-score-bar-fill").forEach(el => {
                    el.style.width = el.dataset.width + "%";
                });
            }, 60);
        });
    }

    // Skill tags
    function renderSkillTags(rec) {
        const matched = rec.matched_skills || [];
        const missing = rec.missing_skills || [];

        matchedSkillsTags.innerHTML = matched.length
            ? matched.map(s =>
                `<span class="cr-tag cr-tag-matched">✓ ${esc(s)}</span>`
              ).join("")
            : `<span style="font-size:13px;color:#bbb;">None matched yet</span>`;

        missingSkillsTags.innerHTML = missing.length
            ? missing.map(s =>
                `<span class="cr-tag cr-tag-missing">+ ${esc(s)}</span>`
              ).join("")
            : `<span style="font-size:13px;color:#2ecc71;font-weight:600;">
                   ✅ All required skills matched!
               </span>`;
    }

    // Roadmap timeline
    function renderRoadmap(rec) {
        const steps = rec.roadmap || [];
        if (steps.length === 0) {
            roadmapList.innerHTML = `<div style="color:#bbb;font-size:13px;">No roadmap available.</div>`;
            return;
        }
        roadmapList.innerHTML = steps.map((step, i) => `
            <div class="cr-roadmap-step">
                <div class="cr-step-num">${i + 1}</div>
                <div class="cr-step-text">${esc(step)}</div>
            </div>`).join("");
    }

    // Cert & course suggestions
    function renderSuggestions(rec) {
        const certs   = rec.cert_suggestions   || [];
        const courses = rec.course_suggestions || [];

        certSuggestions.innerHTML = certs.length
            ? certs.map(c =>
                `<div class="cr-suggestion-item">${esc(c)}</div>`
              ).join("")
            : `<div style="color:#bbb;font-size:13px;">No suggestions.</div>`;

        courseSuggestions.innerHTML = courses.length
            ? courses.map(c =>
                `<div class="cr-suggestion-item">${esc(c)}</div>`
              ).join("")
            : `<div style="color:#bbb;font-size:13px;">No suggestions.</div>`;
    }

    // ── Skill Gaps ────────────────────────────────────────────────────────────

    function renderSkillGaps(gaps) {
        if (!gaps || gaps.length === 0) {
            skillGapsTags.innerHTML =
                `<span style="color:#bbb;font-size:13px;">
                     No significant skill gaps detected — great work!
                 </span>`;
            return;
        }

        // Priority → CSS class mapping
        const cls = {
            "High":   "cr-tag-gap-high",
            "Medium": "cr-tag-gap-medium",
            "Low":    "cr-tag-gap-low",
        };

        skillGapsTags.innerHTML = gaps.map(g => {
            const tagClass  = cls[g.priority] || "cr-tag-gap-low";
            const freqLabel = g.frequency > 1
                ? `needed in ${g.frequency} career paths`
                : "needed in 1 career path";
            return `
            <div class="cr-gap-tag ${tagClass}" title="${freqLabel}">
                ${esc(g.skill_name)}
                <span class="cr-gap-priority">${esc(g.priority)}</span>
            </div>`;
        }).join("");
    }

}); // end DOMContentLoaded
