"""
career_engine.py
-----------------
Phase 4 — Career Recommendation Engine
Smart Career Recommendation System

Pure scoring module — no Flask context, no DB calls.
The Flask route feeds it data; it returns a ranked list
of career objects ready to be stored and returned as JSON.

Scoring model
─────────────
Each career has a required skill set, related interests,
relevant certifications, and GitHub language affinities.

Five independent sub-scores (each 0-100) are combined
into a weighted overall match_percentage:

  skill_score     0.35   (most important: hard technical fit)
  interest_score  0.20   (passion alignment)
  cert_score      0.15   (credentials)
  project_score   0.15   (demonstrated experience via project tech)
  github_score    0.15   (GitHub language & activity evidence)

career_score = same formula but without GitHub (for users
who haven't connected GitHub yet).
"""

import math
from typing import Any


# ══════════════════════════════════════════════════════════════════════════════
# CAREER DEFINITIONS
# ══════════════════════════════════════════════════════════════════════════════

CAREERS: list[dict] = [
    # ── Software Developer ─────────────────────────────────────────────────────
    {
        "title":    "Software Developer",
        "category": "Software Engineering",
        "required_skills": [
            "Python", "Java", "C++", "C#", "JavaScript",
            "Data Structures", "Algorithms", "OOP", "Git",
            "REST API", "SQL", "Testing", "Debugging",
        ],
        "bonus_skills": [
            "Kotlin", "Go", "Ruby", "Swift", "Design Patterns",
            "Agile", "Docker", "Linux",
        ],
        "related_interests": [
            "Software Development", "Programming", "Open Source",
            "Algorithms", "System Design", "Computer Science",
        ],
        "relevant_certs": [
            "Oracle Certified Java Programmer",
            "Microsoft Certified: Azure Developer",
            "AWS Certified Developer",
            "Google Associate Cloud Engineer",
            "Certified Software Development Professional",
        ],
        "github_languages": [
            "Python", "Java", "C++", "C#", "JavaScript", "Go",
            "Kotlin", "Ruby", "Swift", "TypeScript",
        ],
        "roadmap": [
            "Master a primary language deeply (Python or Java recommended)",
            "Study core Data Structures & Algorithms",
            "Build 3-5 solo projects covering CRUD, APIs, and data processing",
            "Learn version control (Git + GitHub) and code review practices",
            "Contribute to an open-source project",
            "Study system design fundamentals (caching, queues, databases)",
            "Practice LeetCode / HackerRank problems regularly",
            "Learn CI/CD basics (GitHub Actions or Jenkins)",
        ],
        "cert_suggestions": [
            "Oracle Certified Java Programmer (OCPJP)",
            "Microsoft Certified: Azure Developer Associate",
            "AWS Certified Developer – Associate",
        ],
        "course_suggestions": [
            "CS50's Introduction to Computer Science (Harvard / edX) — Free",
            "The Complete Python Bootcamp (Udemy — Jose Portilla)",
            "Algorithms Specialization (Coursera — Stanford)",
            "Clean Code by Robert C. Martin (Book)",
            "System Design Interview by Alex Xu (Book)",
        ],
    },

    # ── Full Stack Developer ───────────────────────────────────────────────────
    {
        "title":    "Full Stack Developer",
        "category": "Web Development",
        "required_skills": [
            "HTML", "CSS", "JavaScript", "TypeScript", "React",
            "Node.js", "Python", "SQL", "NoSQL", "REST API",
            "Git", "Docker", "Linux",
        ],
        "bonus_skills": [
            "Vue", "Angular", "Next.js", "GraphQL", "Redis",
            "AWS", "CI/CD", "Testing", "WebSockets",
        ],
        "related_interests": [
            "Web Development", "Full Stack", "JavaScript",
            "UI Design", "APIs", "Cloud Computing",
        ],
        "relevant_certs": [
            "AWS Certified Developer",
            "MongoDB Developer Certification",
            "Meta Front-End Developer Certificate",
            "Meta Back-End Developer Certificate",
            "Google UX Design Certificate",
        ],
        "github_languages": [
            "JavaScript", "TypeScript", "HTML", "CSS", "Python",
            "Vue", "PHP",
        ],
        "roadmap": [
            "Master HTML5, CSS3, and Vanilla JavaScript thoroughly",
            "Learn a frontend framework: React (most in demand) or Vue",
            "Build responsive layouts using Flexbox, Grid, and Tailwind CSS",
            "Learn Node.js + Express for backend API development",
            "Study relational databases (PostgreSQL) and NoSQL (MongoDB)",
            "Containerise projects with Docker",
            "Deploy a full-stack app on AWS or Vercel",
            "Implement authentication (JWT / OAuth2)",
        ],
        "cert_suggestions": [
            "Meta Full Stack Developer Professional Certificate (Coursera)",
            "AWS Certified Developer – Associate",
            "MongoDB Certified Developer Associate",
        ],
        "course_suggestions": [
            "The Web Developer Bootcamp (Udemy — Colt Steele)",
            "Full Stack Open (University of Helsinki) — Free",
            "React — The Complete Guide (Udemy — Maximilian Schwarzmüller)",
            "Node.js, Express, MongoDB & More (Udemy — Jonas Schmedtmann)",
        ],
    },

    # ── Frontend Developer ─────────────────────────────────────────────────────
    {
        "title":    "Frontend Developer",
        "category": "Web Development",
        "required_skills": [
            "HTML", "CSS", "JavaScript", "TypeScript", "React",
            "Responsive Design", "Accessibility", "Git",
            "REST API", "Testing",
        ],
        "bonus_skills": [
            "Vue", "Angular", "Next.js", "Tailwind CSS", "SCSS",
            "Figma", "WebPack", "Performance Optimisation",
        ],
        "related_interests": [
            "UI Design", "Web Development", "User Experience",
            "JavaScript", "Design Systems", "Accessibility",
        ],
        "relevant_certs": [
            "Meta Front-End Developer Certificate",
            "Google UX Design Certificate",
            "W3Schools Front End Certificate",
            "AWS Certified Developer",
        ],
        "github_languages": [
            "JavaScript", "TypeScript", "HTML", "CSS",
            "SCSS", "Svelte", "Vue",
        ],
        "roadmap": [
            "Perfect semantic HTML5 and modern CSS (Grid, Flexbox, Variables)",
            "Master JavaScript ES6+ (async/await, closures, prototypes)",
            "Pick a framework: React with hooks is the industry standard",
            "Learn Figma for design-to-code handoff workflows",
            "Study web performance (Lighthouse, Core Web Vitals)",
            "Implement accessibility (ARIA, keyboard navigation, colour contrast)",
            "Write component tests with Jest + React Testing Library",
            "Build and publish a design system / component library",
        ],
        "cert_suggestions": [
            "Meta Front-End Developer Professional Certificate (Coursera)",
            "Google UX Design Professional Certificate (Coursera)",
        ],
        "course_suggestions": [
            "JavaScript: The Complete Guide (Udemy — Maximilian Schwarzmüller)",
            "React — The Complete Guide (Udemy)",
            "CSS for JavaScript Developers (Josh Comeau) — joshwcomeau.com",
            "Frontend Masters — Complete Intro to React",
        ],
    },

    # ── Backend Developer ──────────────────────────────────────────────────────
    {
        "title":    "Backend Developer",
        "category": "Software Engineering",
        "required_skills": [
            "Python", "Java", "Node.js", "Go", "SQL",
            "REST API", "Microservices", "Docker", "Linux",
            "Authentication", "Caching", "Message Queues", "Git",
        ],
        "bonus_skills": [
            "Kubernetes", "Redis", "RabbitMQ", "Kafka",
            "PostgreSQL", "MongoDB", "gRPC", "AWS",
        ],
        "related_interests": [
            "Backend Development", "APIs", "System Design",
            "Databases", "Cloud Computing", "DevOps",
        ],
        "relevant_certs": [
            "AWS Certified Developer",
            "Google Cloud Professional Developer",
            "Oracle Certified Java Programmer",
            "MongoDB Certified Developer",
        ],
        "github_languages": [
            "Python", "Java", "Go", "Rust", "C#",
            "TypeScript", "Ruby", "PHP",
        ],
        "roadmap": [
            "Master one backend language deeply (Python + FastAPI or Java + Spring)",
            "Understand HTTP deeply: status codes, headers, REST principles",
            "Design and build RESTful APIs with versioning and error handling",
            "Learn relational databases: SQL, indexing, transactions, ORM",
            "Implement authentication: sessions, JWT, OAuth2",
            "Add caching layers with Redis",
            "Study message queues (RabbitMQ / Kafka) for async processing",
            "Containerise with Docker and learn Kubernetes basics",
            "Set up observability: logging, metrics, tracing",
        ],
        "cert_suggestions": [
            "AWS Certified Developer – Associate",
            "Google Cloud Professional Cloud Developer",
            "Oracle Certified Professional Java SE Developer",
        ],
        "course_suggestions": [
            "Python and Django Full Stack Web Developer Bootcamp (Udemy)",
            "Designing RESTful APIs (Udacity)",
            "The Complete Node.js Developer Course (Udemy — Andrew Mead)",
            "Database Engineering Professional Certificate (Meta / Coursera)",
        ],
    },

    # ── AI / ML Engineer ──────────────────────────────────────────────────────
    {
        "title":    "AI Engineer",
        "category": "Artificial Intelligence",
        "required_skills": [
            "Python", "Machine Learning", "Deep Learning",
            "TensorFlow", "PyTorch", "Scikit-learn", "NLP",
            "Mathematics", "Statistics", "SQL", "Data Preprocessing",
            "Model Deployment", "Git",
        ],
        "bonus_skills": [
            "Hugging Face", "LangChain", "RAG", "LLMs",
            "MLflow", "Kubernetes", "AWS SageMaker",
            "Computer Vision", "Time Series",
        ],
        "related_interests": [
            "Artificial Intelligence", "Machine Learning", "Deep Learning",
            "NLP", "Data Science", "Research", "Neural Networks",
        ],
        "relevant_certs": [
            "TensorFlow Developer Certificate",
            "AWS Certified Machine Learning Specialty",
            "Google Professional ML Engineer",
            "DeepLearning.AI Deep Learning Specialization",
            "Databricks Certified Machine Learning Professional",
        ],
        "github_languages": [
            "Python", "Jupyter Notebook", "R", "Julia", "C++",
        ],
        "roadmap": [
            "Solidify Python: NumPy, Pandas, Matplotlib, Seaborn",
            "Study mathematics: Linear Algebra, Calculus, Probability, Statistics",
            "Complete Andrew Ng's ML Specialization on Coursera",
            "Build classical ML projects: regression, classification, clustering",
            "Learn deep learning frameworks (TensorFlow or PyTorch)",
            "Train and fine-tune a transformer model (Hugging Face)",
            "Study MLOps: experiment tracking (MLflow), model serving (FastAPI)",
            "Deploy a model to AWS SageMaker or GCP Vertex AI",
            "Stay current with arXiv papers and implement 1-2 per month",
        ],
        "cert_suggestions": [
            "TensorFlow Developer Certificate (Google)",
            "AWS Certified Machine Learning – Specialty",
            "DeepLearning.AI TensorFlow Developer Professional Certificate",
            "Google Professional Machine Learning Engineer",
        ],
        "course_suggestions": [
            "Machine Learning Specialization (Coursera — Andrew Ng) — auditable free",
            "Deep Learning Specialization (Coursera — deeplearning.ai)",
            "fast.ai Practical Deep Learning for Coders — Free",
            "Hands-On Machine Learning with Scikit-Learn, Keras & TensorFlow (Book)",
            "CS231n: Convolutional Neural Networks (Stanford) — Free",
        ],
    },

    # ── Data Analyst ──────────────────────────────────────────────────────────
    {
        "title":    "Data Analyst",
        "category": "Data & Analytics",
        "required_skills": [
            "SQL", "Python", "Excel", "Statistics", "Data Visualisation",
            "Tableau", "Power BI", "Data Cleaning", "Pandas",
            "Business Intelligence", "Reporting",
        ],
        "bonus_skills": [
            "R", "Machine Learning", "A/B Testing",
            "Looker", "dbt", "Spark", "Airflow",
        ],
        "related_interests": [
            "Data Analysis", "Business Intelligence", "Statistics",
            "Data Visualisation", "Reporting", "Finance", "Marketing Analytics",
        ],
        "relevant_certs": [
            "Google Data Analytics Certificate",
            "Microsoft Power BI Data Analyst",
            "Tableau Desktop Specialist",
            "IBM Data Analyst Professional Certificate",
            "SQL for Data Science (UC Davis / Coursera)",
        ],
        "github_languages": [
            "Python", "R", "SQL", "Jupyter Notebook",
        ],
        "roadmap": [
            "Master SQL: joins, window functions, CTEs, subqueries",
            "Learn Python for data: Pandas, NumPy, Matplotlib, Plotly",
            "Study descriptive statistics and probability",
            "Build dashboards in Tableau or Power BI using real datasets",
            "Practice A/B test analysis and hypothesis testing",
            "Work through Kaggle datasets and publish your analysis",
            "Learn Excel: pivot tables, VLOOKUP, power query",
            "Understand data warehousing concepts (star schema, ETL)",
        ],
        "cert_suggestions": [
            "Google Data Analytics Professional Certificate (Coursera)",
            "Microsoft Certified: Power BI Data Analyst Associate",
            "Tableau Desktop Specialist",
        ],
        "course_suggestions": [
            "Google Data Analytics Certificate (Coursera) — financial aid available",
            "SQL for Data Analysis (Udacity)",
            "Python for Data Analysis (Wes McKinney — Book)",
            "Storytelling with Data (Cole Nussbaumer Knaflic — Book)",
            "Statistics with Python Specialization (Coursera — University of Michigan)",
        ],
    },

    # ── Cloud Engineer ─────────────────────────────────────────────────────────
    {
        "title":    "Cloud Engineer",
        "category": "Cloud & DevOps",
        "required_skills": [
            "AWS", "Azure", "GCP", "Linux", "Docker",
            "Kubernetes", "Terraform", "CI/CD", "Networking",
            "Infrastructure as Code", "Security", "Python", "Bash",
        ],
        "bonus_skills": [
            "Ansible", "Helm", "Prometheus", "Grafana",
            "Pulumi", "Cost Optimisation", "Serverless",
        ],
        "related_interests": [
            "Cloud Computing", "DevOps", "Infrastructure",
            "Automation", "Site Reliability", "Networking",
        ],
        "relevant_certs": [
            "AWS Solutions Architect Associate",
            "AWS Certified Cloud Practitioner",
            "Google Associate Cloud Engineer",
            "Microsoft Azure Administrator (AZ-104)",
            "Certified Kubernetes Administrator (CKA)",
            "HashiCorp Terraform Associate",
        ],
        "github_languages": [
            "Python", "Bash", "Go", "HCL", "YAML",
            "Dockerfile", "Shell",
        ],
        "roadmap": [
            "Understand core networking: TCP/IP, DNS, load balancers, VPNs",
            "Get comfortable with Linux: file system, processes, shell scripting",
            "Learn a cloud platform deeply: AWS is most in-demand",
            "Pass AWS Cloud Practitioner to build a solid foundation",
            "Master Docker: images, containers, volumes, networking",
            "Learn Kubernetes: pods, deployments, services, ingress",
            "Automate infrastructure with Terraform",
            "Build a CI/CD pipeline (GitHub Actions → Docker → EKS)",
            "Study cloud security: IAM, VPC, encryption, compliance",
        ],
        "cert_suggestions": [
            "AWS Certified Solutions Architect – Associate (SAA-C03)",
            "HashiCorp Certified: Terraform Associate",
            "Certified Kubernetes Administrator (CKA)",
            "Google Associate Cloud Engineer",
        ],
        "course_suggestions": [
            "Ultimate AWS Certified Solutions Architect Associate (Udemy — Stephane Maarek)",
            "Docker & Kubernetes: The Practical Guide (Udemy — Maximilian Schwarzmüller)",
            "Terraform for Beginners (freeCodeCamp) — Free",
            "Linux Command Line Basics (Udacity) — Free",
            "Cloud Computing Specialization (Coursera — University of Illinois)",
        ],
    },

    # ── Cybersecurity Analyst ─────────────────────────────────────────────────
    {
        "title":    "Cybersecurity Analyst",
        "category": "Cybersecurity",
        "required_skills": [
            "Network Security", "Linux", "Python", "SIEM",
            "Threat Analysis", "Incident Response", "Penetration Testing",
            "Firewalls", "Cryptography", "Vulnerability Assessment",
            "OWASP", "Log Analysis",
        ],
        "bonus_skills": [
            "Ethical Hacking", "Malware Analysis", "Splunk",
            "Wireshark", "Metasploit", "Cloud Security",
            "Digital Forensics", "Zero Trust",
        ],
        "related_interests": [
            "Cybersecurity", "Ethical Hacking", "Networking",
            "Privacy", "Forensics", "Cryptography", "Threat Intelligence",
        ],
        "relevant_certs": [
            "CompTIA Security+",
            "CompTIA Network+",
            "Certified Ethical Hacker (CEH)",
            "CISSP",
            "CISM",
            "Google Cybersecurity Certificate",
            "Offensive Security OSCP",
        ],
        "github_languages": [
            "Python", "Bash", "PowerShell", "Go", "C",
            "Shell",
        ],
        "roadmap": [
            "Build a strong networking foundation: OSI model, TCP/IP, protocols",
            "Get comfortable with Linux and Windows administration",
            "Learn basic Python scripting for security automation",
            "Study core security concepts: CIA triad, threat models, authentication",
            "Set up a home lab (VirtualBox + Kali Linux + Metasploitable)",
            "Practice on TryHackMe and HackTheBox platforms",
            "Earn CompTIA Security+ as the entry-level industry standard",
            "Learn SIEM tools: Splunk or Microsoft Sentinel",
            "Study incident response: detection → containment → eradication → recovery",
            "Work towards CEH or OSCP for penetration testing specialisation",
        ],
        "cert_suggestions": [
            "CompTIA Security+ (SY0-701) — entry-level industry benchmark",
            "Google Cybersecurity Professional Certificate (Coursera)",
            "Certified Ethical Hacker (CEH) — EC-Council",
            "Offensive Security Certified Professional (OSCP) — advanced",
        ],
        "course_suggestions": [
            "Google Cybersecurity Professional Certificate (Coursera) — financial aid",
            "The Complete Cyber Security Course (Udemy — Nathan House)",
            "TryHackMe Learning Paths — try.hackme.com — Free tier",
            "Cybersecurity Specialization (Coursera — University of Maryland)",
            "Penetration Testing with Kali Linux (OffSec) — advanced",
        ],
    },
]


# ══════════════════════════════════════════════════════════════════════════════
# SCORING HELPERS
# ══════════════════════════════════════════════════════════════════════════════

# Proficiency multipliers applied to skill matching
PROFICIENCY_WEIGHTS = {
    "Expert":       1.00,
    "Advanced":     0.85,
    "Intermediate": 0.65,
    "Beginner":     0.35,
}

# Sub-score weights
W_SKILL     = 0.35
W_INTEREST  = 0.20
W_CERT      = 0.15
W_PROJECT   = 0.15
W_GITHUB    = 0.15


def _clamp(val: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, float(val)))


def _normalise(hit_weight: float, total_weight: float) -> float:
    """Ratio of accumulated weight to max possible weight → 0-100."""
    if total_weight <= 0:
        return 0.0
    return _clamp((hit_weight / total_weight) * 100)


def _fuzzy_match(term: str, corpus: list[str]) -> bool:
    """
    Case-insensitive substring match.
    'React' matches 'React Native', 'React.js', etc.
    """
    t = term.lower()
    return any(t in item.lower() or item.lower() in t for item in corpus)


# ── Skill score ────────────────────────────────────────────────────────────────

def _skill_score(
    user_skills: list[dict],      # [{"skill_name": ..., "proficiency": ...}]
    required: list[str],
    bonus: list[str],
) -> tuple[float, list[str], list[str]]:
    """
    Returns (score_0_100, matched_skill_names, missing_skill_names).

    Required skills: each worth 1.0 × proficiency_weight.
    Bonus skills: each worth 0.4 × proficiency_weight (extra credit).
    """
    skill_names = [s["skill_name"] for s in user_skills]
    prof_map    = {s["skill_name"].lower(): PROFICIENCY_WEIGHTS.get(s.get("proficiency", "Beginner"), 0.35)
                   for s in user_skills}

    matched: list[str] = []
    missing: list[str] = []
    hit_w   = 0.0
    max_w   = float(len(required))  # max possible weight from required skills

    for req in required:
        if _fuzzy_match(req, skill_names):
            matched.append(req)
            # Find the actual matched skill name to look up proficiency
            pkey = next((s.lower() for s in skill_names
                         if req.lower() in s.lower() or s.lower() in req.lower()), req.lower())
            hit_w += prof_map.get(pkey, 0.35)
        else:
            missing.append(req)

    # Bonus skills give extra credit capped at 20% bonus on top of base
    bonus_w = 0.0
    for bon in bonus:
        if _fuzzy_match(bon, skill_names):
            pkey = next((s.lower() for s in skill_names
                         if bon.lower() in s.lower() or s.lower() in bon.lower()), bon.lower())
            bonus_w += prof_map.get(pkey, 0.35) * 0.4

    # Base score
    base  = _normalise(hit_w, max_w) if max_w > 0 else 0.0
    bonus_score = _clamp((bonus_w / max(len(bonus), 1)) * 20) if bonus else 0.0
    score = _clamp(base + bonus_score)
    return score, matched, missing


# ── Interest score ─────────────────────────────────────────────────────────────

def _interest_score(
    user_interests: list[str],    # plain interest name strings
    related: list[str],
) -> float:
    if not related:
        return 50.0   # neutral if career has no specific interest mapping
    hits = sum(1 for ri in related if _fuzzy_match(ri, user_interests))
    return _clamp((hits / len(related)) * 100)


# ── Certification score ────────────────────────────────────────────────────────

def _cert_score(
    user_certs: list[str],        # certification name strings
    relevant: list[str],
) -> float:
    if not relevant:
        return 0.0
    hits = sum(1 for rc in relevant if _fuzzy_match(rc, user_certs))
    # Even one matching cert is a strong signal, so use log scaling
    raw = math.log1p(hits) / math.log1p(len(relevant)) * 100
    return _clamp(raw)


# ── Project score ──────────────────────────────────────────────────────────────

def _project_score(
    project_technologies: list[str],  # all tech strings from projects
    required_skills: list[str],
    bonus_skills: list[str],
) -> float:
    """
    Checks how many career-relevant skills appear in the user's project tech stacks.
    """
    if not project_technologies:
        return 0.0
    all_career_skills = required_skills + bonus_skills
    hits = sum(1 for skill in all_career_skills
               if _fuzzy_match(skill, project_technologies))
    return _clamp((hits / len(all_career_skills)) * 100)


# ── GitHub score ───────────────────────────────────────────────────────────────

def _github_score(
    github_languages: list[str],   # languages detected in GitHub repos
    career_languages: list[str],
    github_activity: float,        # overall_score from Phase 3 (0-100)
) -> float:
    """
    Combines language affinity with overall GitHub activity level.
    Language match contributes 70%, activity level 30%.
    """
    if not github_languages and github_activity == 0:
        return 0.0

    lang_hits = sum(1 for cl in career_languages
                    if _fuzzy_match(cl, github_languages))
    lang_score = _clamp((lang_hits / max(len(career_languages), 1)) * 100)

    activity_score = _clamp(github_activity)

    return _clamp(lang_score * 0.70 + activity_score * 0.30)


# ── Skill gap aggregation ──────────────────────────────────────────────────────

def _compute_skill_gaps(recommendations: list[dict]) -> list[dict]:
    """
    Aggregates missing skills across the top-5 recommendations.
    Skills missing from more careers get higher priority.
    """
    freq: dict[str, int] = {}
    for rec in recommendations[:5]:
        for skill in rec.get("missing_skills", []):
            freq[skill] = freq.get(skill, 0) + 1

    gaps = []
    for skill, count in sorted(freq.items(), key=lambda x: -x[1]):
        if count >= 3:
            priority = "High"
        elif count >= 2:
            priority = "Medium"
        else:
            priority = "Low"
        gaps.append({"skill_name": skill, "frequency": count, "priority": priority})

    return gaps


# ══════════════════════════════════════════════════════════════════════════════
# MAIN PUBLIC FUNCTION
# ══════════════════════════════════════════════════════════════════════════════

def generate_recommendations(user_data: dict[str, Any]) -> dict[str, Any]:
    """
    Entry point called by the Flask route.

    user_data dict keys
    ───────────────────
    skills        list[{"skill_name": str, "proficiency": str}]
    interests     list[str]           — interest_name values
    certifications list[str]          — certification_name values
    project_tech  list[str]           — all technologies_used strings (flat)
    github_languages list[str]        — top languages from Phase 3
    github_activity_score float       — overall_score from github_analysis

    Returns
    ───────
    {
      "recommendations": [ {...}, ...],   # ranked, all 8 careers
      "skill_gaps": [ {...}, ...],
    }
    """
    skills         = user_data.get("skills", [])
    interests      = user_data.get("interests", [])
    certs          = user_data.get("certifications", [])
    proj_tech      = user_data.get("project_tech", [])
    gh_langs       = user_data.get("github_languages", [])
    gh_activity    = float(user_data.get("github_activity_score", 0) or 0)
    has_github     = bool(gh_langs) or gh_activity > 0

    results = []

    for career in CAREERS:
        # ── Individual sub-scores ─────────────────────────────────────────────
        skill_sc, matched, missing = _skill_score(
            skills,
            career["required_skills"],
            career["bonus_skills"],
        )
        interest_sc = _interest_score(interests, career["related_interests"])
        cert_sc     = _cert_score(certs, career["relevant_certs"])
        project_sc  = _project_score(proj_tech, career["required_skills"], career["bonus_skills"])
        github_sc   = _github_score(gh_langs, career["github_languages"], gh_activity)

        # ── Weighted overall ──────────────────────────────────────────────────
        if has_github:
            match_pct = (
                skill_sc    * W_SKILL    +
                interest_sc * W_INTEREST +
                cert_sc     * W_CERT     +
                project_sc  * W_PROJECT  +
                github_sc   * W_GITHUB
            )
            career_sc = (
                skill_sc    * (W_SKILL    / (1 - W_GITHUB)) +
                interest_sc * (W_INTEREST / (1 - W_GITHUB)) +
                cert_sc     * (W_CERT     / (1 - W_GITHUB)) +
                project_sc  * (W_PROJECT  / (1 - W_GITHUB))
            )
        else:
            # GitHub not connected — redistribute weight proportionally
            total_w = W_SKILL + W_INTEREST + W_CERT + W_PROJECT
            match_pct = (
                skill_sc    * (W_SKILL    / total_w) +
                interest_sc * (W_INTEREST / total_w) +
                cert_sc     * (W_CERT     / total_w) +
                project_sc  * (W_PROJECT  / total_w)
            )
            career_sc = match_pct
            github_sc = 0.0

        match_pct = _clamp(match_pct)
        career_sc = _clamp(career_sc)

        results.append({
            "career_title":    career["title"],
            "career_category": career["category"],
            "match_percentage":  round(match_pct, 2),
            "skill_score":       round(skill_sc,    2),
            "interest_score":    round(interest_sc, 2),
            "cert_score":        round(cert_sc,     2),
            "project_score":     round(project_sc,  2),
            "github_score":      round(github_sc,   2),
            "career_score":      round(career_sc,   2),
            "matched_skills":    matched,
            "missing_skills":    missing,
            "roadmap":           career["roadmap"],
            "cert_suggestions":  career["cert_suggestions"],
            "course_suggestions": career["course_suggestions"],
        })

    # ── Rank by match_percentage descending ───────────────────────────────────
    results.sort(key=lambda r: r["match_percentage"], reverse=True)
    for i, r in enumerate(results):
        r["rank_position"] = i + 1

    # ── Skill gaps across top-5 ───────────────────────────────────────────────
    gaps = _compute_skill_gaps(results)

    return {
        "recommendations": results,
        "skill_gaps":       gaps,
    }
