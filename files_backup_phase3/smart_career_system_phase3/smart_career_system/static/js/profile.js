/* =====================================================
   profile.js
   Handles the Student Profile page for the Smart Career
   Recommendation System — Phase 2.

   Sections handled:
     1. Personal Info   — GET + POST /api/profile
     2. Skills          — GET /api/skills, POST /api/skills,
                          PUT /api/skills/:id, DELETE /api/skills/:id
     3. Interests       — GET /api/interests, POST /api/interests,
                          DELETE /api/interests/:id
     4. Certifications  — GET /api/certifications, POST /api/certifications,
                          DELETE /api/certifications/:id
     5. Projects        — GET /api/projects, POST /api/projects,
                          DELETE /api/projects/:id
   ===================================================== */

document.addEventListener("DOMContentLoaded", function () {

    // ─────────────────────────────────────────
    // Side-nav tab switching
    // ─────────────────────────────────────────
    const navLinks   = document.querySelectorAll(".sidenav-link");
    const sections   = document.querySelectorAll(".profile-section");

    navLinks.forEach(link => {
        link.addEventListener("click", function () {
            navLinks.forEach(l => l.classList.remove("active"));
            sections.forEach(s => s.classList.remove("active"));
            this.classList.add("active");
            document.getElementById("section-" + this.dataset.section).classList.add("active");
        });
    });

    // ─────────────────────────────────────────
    // Shared helpers
    // ─────────────────────────────────────────

    /** POST/PUT/DELETE JSON to the given URL and return parsed JSON. */
    async function apiRequest(url, method = "GET", body = null) {
        const opts = {
            method,
            headers: { "Content-Type": "application/json" }
        };
        if (body !== null) opts.body = JSON.stringify(body);
        const res = await fetch(url, opts);
        return res.json();
    }

    /** Show an inline error message in a given element by id. */
    function setError(elId, msg) {
        const el = document.getElementById(elId);
        if (el) el.textContent = msg || "";
    }

    /** Show a named alert box with success/error styling. */
    function showAlert(elId, message, type = "error") {
        const el = document.getElementById(elId);
        if (!el) return;
        el.textContent = message;
        el.className = "alert-box " + type;
    }

    function hideAlert(elId) {
        const el = document.getElementById(elId);
        if (el) el.className = "alert-box hidden";
    }

    /** Format a YYYY-MM-DD string as a human-friendly date, or return "—". */
    function fmtDate(iso) {
        if (!iso) return "—";
        const [y, m, d] = iso.split("-");
        const months = ["Jan","Feb","Mar","Apr","May","Jun",
                        "Jul","Aug","Sep","Oct","Nov","Dec"];
        return `${months[parseInt(m,10)-1]} ${parseInt(d,10)}, ${y}`;
    }

    /** Show a transient "Saved ✓" message next to the save button. */
    function flashSaveStatus(elId, message = "Saved ✓", isError = false) {
        const el = document.getElementById(elId);
        if (!el) return;
        el.textContent = message;
        el.className = "save-status visible" + (isError ? " error" : "");
        setTimeout(() => { el.className = "save-status"; }, 3000);
    }

    // ─────────────────────────────────────────
    // Bootstrap: load everything on page load
    // ─────────────────────────────────────────
    loadPersonalInfo();
    loadSkills();
    loadInterests();
    loadCertifications();
    loadProjects();


    // ═══════════════════════════════════════════════════════
    // SECTION 1 — Personal Info
    // ═══════════════════════════════════════════════════════

    async function loadPersonalInfo() {
        try {
            const data = await apiRequest("/api/profile");
            if (!data.success) return;

            const acct = data.account || {};
            const prof = data.profile || {};

            // Read-only account fields
            document.getElementById("display_full_name").value = acct.full_name || "";
            document.getElementById("display_email").value     = acct.email    || "";
            document.getElementById("display_username").value  = acct.username || "";

            // Editable profile fields
            document.getElementById("phone").value            = prof.phone            || "";
            document.getElementById("date_of_birth").value    = prof.date_of_birth    || "";
            document.getElementById("graduation_year").value  = prof.graduation_year  || "";
            document.getElementById("institution_name").value = prof.institution_name || "";
            document.getElementById("field_of_study").value   = prof.field_of_study   || "";
            document.getElementById("linkedin_url").value     = prof.linkedin_url     || "";
            document.getElementById("github_url").value       = prof.github_url       || "";
            document.getElementById("bio").value              = prof.bio              || "";

            setSelectValue("gender",          prof.gender);
            setSelectValue("education_level", prof.education_level);

        } catch (err) {
            console.error("loadPersonalInfo:", err);
        }
    }

    function setSelectValue(id, value) {
        const el = document.getElementById(id);
        if (!el || !value) return;
        for (const opt of el.options) {
            if (opt.value === value) { opt.selected = true; break; }
        }
    }

    document.getElementById("personalForm").addEventListener("submit", async function (e) {
        e.preventDefault();
        hideAlert("personalAlert");

        const saveBtn = document.getElementById("savePersonalBtn");
        saveBtn.disabled = true;
        saveBtn.textContent = "Saving...";

        const payload = {
            phone:            document.getElementById("phone").value.trim(),
            date_of_birth:    document.getElementById("date_of_birth").value,
            gender:           document.getElementById("gender").value,
            education_level:  document.getElementById("education_level").value,
            institution_name: document.getElementById("institution_name").value.trim(),
            field_of_study:   document.getElementById("field_of_study").value.trim(),
            graduation_year:  document.getElementById("graduation_year").value,
            linkedin_url:     document.getElementById("linkedin_url").value.trim(),
            github_url:       document.getElementById("github_url").value.trim(),
            bio:              document.getElementById("bio").value.trim(),
        };

        try {
            const data = await apiRequest("/api/profile", "POST", payload);
            if (data.success) {
                flashSaveStatus("personalSaveStatus", "Saved ✓", false);
            } else {
                showAlert("personalAlert", data.message || "Could not save profile.", "error");
            }
        } catch (err) {
            showAlert("personalAlert", "Network error. Please try again.", "error");
        } finally {
            saveBtn.disabled = false;
            saveBtn.textContent = "Save Profile";
        }
    });


    // ═══════════════════════════════════════════════════════
    // SECTION 2 — Skills
    // ═══════════════════════════════════════════════════════

    async function loadSkills() {
        try {
            const data = await apiRequest("/api/skills");
            if (!data.success) return;
            renderSkills(data.skills);
        } catch (err) {
            console.error("loadSkills:", err);
        }
    }

    function renderSkills(skills) {
        const container = document.getElementById("skillsContainer");
        if (!skills || skills.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">🛠️</div>
                    <div>No skills added yet.</div>
                </div>`;
            return;
        }
        container.innerHTML = skills.map(s => skillTag(s)).join("");
        // Attach delete listeners
        container.querySelectorAll(".tag-remove").forEach(btn => {
            btn.addEventListener("click", () => deleteSkill(parseInt(btn.dataset.id)));
        });
        // Attach proficiency change listeners
        container.querySelectorAll(".skill-prof-select").forEach(sel => {
            sel.addEventListener("change", () => updateSkill(parseInt(sel.dataset.id), sel.value));
        });
    }

    function skillTag(s) {
        const profColors = {
            "Beginner":     "#aad4f5",
            "Intermediate": "#7ab8ea",
            "Advanced":     "#3e8fcc",
            "Expert":       "#1b5e8c"
        };
        return `
        <span class="tag tag-skill">
            ${escHtml(s.skill_name)}
            <select class="skill-prof-select"
                    data-id="${s.id}"
                    style="
                        border:none;
                        background:transparent;
                        font-size:11px;
                        font-weight:700;
                        color:${profColors[s.proficiency] || '#888'};
                        cursor:pointer;
                        outline:none;
                        padding:0 2px;
                    "
                    title="Change proficiency">
                ${["Beginner","Intermediate","Advanced","Expert"].map(p =>
                    `<option value="${p}" ${p === s.proficiency ? "selected" : ""}>${p}</option>`
                ).join("")}
            </select>
            <button class="tag-remove" data-id="${s.id}" title="Remove skill">×</button>
        </span>`;
    }

    document.getElementById("addSkillBtn").addEventListener("click", async function () {
        setError("skillError", "");
        const name   = document.getElementById("newSkillName").value.trim();
        const prof   = document.getElementById("newSkillProficiency").value;
        const addBtn = this;

        if (!name) { setError("skillError", "Please enter a skill name."); return; }

        addBtn.disabled = true;
        addBtn.textContent = "Adding...";

        try {
            const data = await apiRequest("/api/skills", "POST", { skill_name: name, proficiency: prof });
            if (data.success) {
                document.getElementById("newSkillName").value = "";
                loadSkills();
            } else {
                setError("skillError", data.message || "Could not add skill.");
            }
        } catch (err) {
            setError("skillError", "Network error.");
        } finally {
            addBtn.disabled = false;
            addBtn.textContent = "+ Add Skill";
        }
    });

    document.getElementById("newSkillName").addEventListener("keydown", function (e) {
        if (e.key === "Enter") { e.preventDefault(); document.getElementById("addSkillBtn").click(); }
    });

    async function updateSkill(skillId, proficiency) {
        try {
            const data = await apiRequest(`/api/skills/${skillId}`, "PUT", { proficiency });
            if (!data.success) {
                console.warn("Update skill failed:", data.message);
                loadSkills(); // revert visual
            }
        } catch (err) {
            console.error("updateSkill:", err);
            loadSkills();
        }
    }

    async function deleteSkill(skillId) {
        try {
            const data = await apiRequest(`/api/skills/${skillId}`, "DELETE");
            if (data.success) loadSkills();
            else setError("skillError", data.message || "Could not delete skill.");
        } catch (err) {
            setError("skillError", "Network error.");
        }
    }


    // ═══════════════════════════════════════════════════════
    // SECTION 3 — Interests
    // ═══════════════════════════════════════════════════════

    async function loadInterests() {
        try {
            const data = await apiRequest("/api/interests");
            if (!data.success) return;
            renderInterests(data.interests);
        } catch (err) {
            console.error("loadInterests:", err);
        }
    }

    function renderInterests(interests) {
        const container = document.getElementById("interestsContainer");
        if (!interests || interests.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">💡</div>
                    <div>No interests added yet.</div>
                </div>`;
            return;
        }
        container.innerHTML = interests.map(i => `
            <span class="tag tag-interest">
                ${escHtml(i.interest_name)}
                <button class="tag-remove" data-id="${i.id}" title="Remove interest">×</button>
            </span>`).join("");

        container.querySelectorAll(".tag-remove").forEach(btn => {
            btn.addEventListener("click", () => deleteInterest(parseInt(btn.dataset.id)));
        });
    }

    document.getElementById("addInterestBtn").addEventListener("click", async function () {
        setError("interestError", "");
        const name   = document.getElementById("newInterestName").value.trim();
        const addBtn = this;

        if (!name) { setError("interestError", "Please enter an interest."); return; }

        addBtn.disabled = true;
        addBtn.textContent = "Adding...";

        try {
            const data = await apiRequest("/api/interests", "POST", { interest_name: name });
            if (data.success) {
                document.getElementById("newInterestName").value = "";
                loadInterests();
            } else {
                setError("interestError", data.message || "Could not add interest.");
            }
        } catch (err) {
            setError("interestError", "Network error.");
        } finally {
            addBtn.disabled = false;
            addBtn.textContent = "+ Add Interest";
        }
    });

    document.getElementById("newInterestName").addEventListener("keydown", function (e) {
        if (e.key === "Enter") { e.preventDefault(); document.getElementById("addInterestBtn").click(); }
    });

    async function deleteInterest(interestId) {
        try {
            const data = await apiRequest(`/api/interests/${interestId}`, "DELETE");
            if (data.success) loadInterests();
            else setError("interestError", data.message || "Could not delete interest.");
        } catch (err) {
            setError("interestError", "Network error.");
        }
    }


    // ═══════════════════════════════════════════════════════
    // SECTION 4 — Certifications
    // ═══════════════════════════════════════════════════════

    const certFormPanel   = document.getElementById("certFormPanel");
    const showCertFormBtn = document.getElementById("showCertFormBtn");
    const cancelCertBtn   = document.getElementById("cancelCertBtn");

    showCertFormBtn.addEventListener("click", () => {
        certFormPanel.style.display = "block";
        setError("certError", "");
        document.getElementById("certName").focus();
    });

    cancelCertBtn.addEventListener("click", () => {
        certFormPanel.style.display = "none";
        clearCertForm();
    });

    function clearCertForm() {
        ["certName","certOrg","certUrl","certIssueDate","certExpiryDate"]
            .forEach(id => { document.getElementById(id).value = ""; });
        setError("certError", "");
    }

    async function loadCertifications() {
        try {
            const data = await apiRequest("/api/certifications");
            if (!data.success) return;
            renderCertifications(data.certifications);
        } catch (err) {
            console.error("loadCertifications:", err);
        }
    }

    function renderCertifications(certs) {
        const container = document.getElementById("certsContainer");
        if (!certs || certs.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">📜</div>
                    <div>No certifications added yet.</div>
                </div>`;
            return;
        }
        container.innerHTML = certs.map(c => `
            <div class="item-card">
                <div class="item-card-body">
                    <div class="item-card-title">${escHtml(c.certification_name)}</div>
                    ${c.issuing_organization
                        ? `<div class="item-card-sub">🏢 ${escHtml(c.issuing_organization)}</div>`
                        : ""}
                    <div class="item-card-meta">
                        ${c.issue_date  ? `Issued: ${fmtDate(c.issue_date)}` : ""}
                        ${c.issue_date && c.expiry_date ? " &nbsp;·&nbsp; " : ""}
                        ${c.expiry_date ? `Expires: ${fmtDate(c.expiry_date)}` : ""}
                        ${c.credential_url
                            ? ` &nbsp;·&nbsp; <a href="${escHtml(c.credential_url)}" target="_blank" rel="noopener">View Credential ↗</a>`
                            : ""}
                    </div>
                </div>
                <button class="btn-delete cert-del-btn" data-id="${c.id}">✕ Remove</button>
            </div>`).join("");

        container.querySelectorAll(".cert-del-btn").forEach(btn => {
            btn.addEventListener("click", () => deleteCertification(parseInt(btn.dataset.id)));
        });
    }

    document.getElementById("saveCertBtn").addEventListener("click", async function () {
        setError("certError", "");
        const name = document.getElementById("certName").value.trim();
        if (!name) { setError("certError", "Certification name is required."); return; }

        const saveBtn = this;
        saveBtn.disabled = true;
        saveBtn.textContent = "Saving...";

        const payload = {
            certification_name:   name,
            issuing_organization: document.getElementById("certOrg").value.trim(),
            credential_url:       document.getElementById("certUrl").value.trim(),
            issue_date:           document.getElementById("certIssueDate").value,
            expiry_date:          document.getElementById("certExpiryDate").value,
        };

        try {
            const data = await apiRequest("/api/certifications", "POST", payload);
            if (data.success) {
                clearCertForm();
                certFormPanel.style.display = "none";
                loadCertifications();
            } else {
                setError("certError", data.message || "Could not save certification.");
            }
        } catch (err) {
            setError("certError", "Network error.");
        } finally {
            saveBtn.disabled = false;
            saveBtn.textContent = "Save Certification";
        }
    });

    async function deleteCertification(certId) {
        try {
            const data = await apiRequest(`/api/certifications/${certId}`, "DELETE");
            if (data.success) loadCertifications();
            else setError("certError", data.message || "Could not delete.");
        } catch (err) {
            setError("certError", "Network error.");
        }
    }


    // ═══════════════════════════════════════════════════════
    // SECTION 5 — Projects
    // ═══════════════════════════════════════════════════════

    const projFormPanel      = document.getElementById("projectFormPanel");
    const showProjectFormBtn = document.getElementById("showProjectFormBtn");
    const cancelProjectBtn   = document.getElementById("cancelProjectBtn");
    const projOngoingChk     = document.getElementById("projOngoing");
    const projEndDateInput   = document.getElementById("projEndDate");

    showProjectFormBtn.addEventListener("click", () => {
        projFormPanel.style.display = "block";
        setError("projectError", "");
        document.getElementById("projTitle").focus();
    });

    cancelProjectBtn.addEventListener("click", () => {
        projFormPanel.style.display = "none";
        clearProjectForm();
    });

    // Disable end date when "ongoing" is checked
    projOngoingChk.addEventListener("change", function () {
        projEndDateInput.disabled = this.checked;
        if (this.checked) projEndDateInput.value = "";
    });

    function clearProjectForm() {
        ["projTitle","projDesc","projTech","projUrl","projStartDate","projEndDate"]
            .forEach(id => { document.getElementById(id).value = ""; });
        projOngoingChk.checked   = false;
        projEndDateInput.disabled = false;
        setError("projectError", "");
    }

    async function loadProjects() {
        try {
            const data = await apiRequest("/api/projects");
            if (!data.success) return;
            renderProjects(data.projects);
        } catch (err) {
            console.error("loadProjects:", err);
        }
    }

    function renderProjects(projects) {
        const container = document.getElementById("projectsContainer");
        if (!projects || projects.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">🚀</div>
                    <div>No projects added yet.</div>
                </div>`;
            return;
        }
        container.innerHTML = projects.map(p => {
            const dateRange = p.start_date
                ? `${fmtDate(p.start_date)} → ${p.is_ongoing ? "Present" : fmtDate(p.end_date)}`
                : "";
            return `
            <div class="item-card">
                <div class="item-card-body">
                    <div class="item-card-title">${escHtml(p.project_title)}</div>
                    ${p.description ? `<div class="item-card-sub">${escHtml(p.description)}</div>` : ""}
                    ${p.technologies_used
                        ? `<div class="item-card-sub" style="margin-top:4px;">
                               🛠 <em>${escHtml(p.technologies_used)}</em>
                           </div>`
                        : ""}
                    <div class="item-card-meta" style="margin-top:6px;">
                        ${dateRange ? `📅 ${dateRange}` : ""}
                        ${p.project_url
                            ? `${dateRange ? " &nbsp;·&nbsp; " : ""}
                               <a href="${escHtml(p.project_url)}" target="_blank" rel="noopener">View Project ↗</a>`
                            : ""}
                    </div>
                </div>
                <button class="btn-delete proj-del-btn" data-id="${p.id}">✕ Remove</button>
            </div>`;
        }).join("");

        container.querySelectorAll(".proj-del-btn").forEach(btn => {
            btn.addEventListener("click", () => deleteProject(parseInt(btn.dataset.id)));
        });
    }

    document.getElementById("saveProjectBtn").addEventListener("click", async function () {
        setError("projectError", "");
        const title = document.getElementById("projTitle").value.trim();
        if (!title) { setError("projectError", "Project title is required."); return; }

        const saveBtn = this;
        saveBtn.disabled = true;
        saveBtn.textContent = "Saving...";

        const isOngoing = projOngoingChk.checked;
        const payload = {
            project_title:     title,
            description:       document.getElementById("projDesc").value.trim(),
            technologies_used: document.getElementById("projTech").value.trim(),
            project_url:       document.getElementById("projUrl").value.trim(),
            start_date:        document.getElementById("projStartDate").value,
            end_date:          isOngoing ? "" : document.getElementById("projEndDate").value,
            is_ongoing:        isOngoing,
        };

        try {
            const data = await apiRequest("/api/projects", "POST", payload);
            if (data.success) {
                clearProjectForm();
                projFormPanel.style.display = "none";
                loadProjects();
            } else {
                setError("projectError", data.message || "Could not save project.");
            }
        } catch (err) {
            setError("projectError", "Network error.");
        } finally {
            saveBtn.disabled = false;
            saveBtn.textContent = "Save Project";
        }
    });

    async function deleteProject(projectId) {
        try {
            const data = await apiRequest(`/api/projects/${projectId}`, "DELETE");
            if (data.success) loadProjects();
            else setError("projectError", data.message || "Could not delete project.");
        } catch (err) {
            setError("projectError", "Network error.");
        }
    }

    // ─────────────────────────────────────────
    // Utility: safely escape HTML
    // ─────────────────────────────────────────
    function escHtml(str) {
        if (!str) return "";
        return String(str)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#39;");
    }

}); // end DOMContentLoaded
