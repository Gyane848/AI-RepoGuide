import streamlit as st
import streamlit.components.v1 as components
from github_client import fetch_repo_data
from analyzer import analyze_repo

st.set_page_config(page_title="AI RepoGuide", page_icon="🧭", layout="centered")

if "show_confetti" not in st.session_state:
    st.session_state.show_confetti = False

# ---------- Global Styling ----------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@500;700;800&family=Inter:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .block-container {
        padding-top: 3rem;
        max-width: 800px;
        position: relative;
    }

    @keyframes shine {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(14px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes cardFadeIn {
        from { opacity: 0; transform: translateY(10px) scale(0.98); }
        to { opacity: 1; transform: translateY(0) scale(1); }
    }
    @keyframes twinkle {
        0%, 100% { opacity: 0.15; transform: scale(0.8); }
        50% { opacity: 0.9; transform: scale(1.1); }
    }
    @keyframes pulseGlow {
        0%, 100% { box-shadow: 0 0 0 0 rgba(255, 138, 92, 0.35); }
        50% { box-shadow: 0 0 0 10px rgba(255, 138, 92, 0); }
    }

    .sparkle {
        position: fixed;
        font-size: 1rem;
        color: #ffb86c;
        animation: twinkle 2.6s ease-in-out infinite;
        pointer-events: none;
        z-index: 0;
    }

    .header-wrap {
        text-align: center !important;
        margin-bottom: 1.6rem;
        width: 100%;
        position: relative;
        z-index: 1;
    }

    .title-row {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1rem;
    }
    .github-icon {
        width: 34px;
        height: 34px;
        opacity: 0.85;
        flex-shrink: 0;
    }

    .main-title {
        font-family: 'Poppins', sans-serif;
        font-size: 2.7rem;
        font-weight: 800;
        text-align: center !important;
        background: linear-gradient(90deg, #ff6a6a, #ffb86c, #ff6a6a, #ffb86c);
        background-size: 300% 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shine 4s ease-in-out infinite;
        margin: 0;
    }

    .subtitle {
        font-size: 1rem;
        color: #c4c4c4;
        line-height: 1.7;
        max-width: 480px;
        margin: 0.9rem auto 0 auto !important;
        text-align: center !important;
        display: block;
        opacity: 0;
        animation: fadeInUp 0.9s ease forwards;
        animation-delay: 2s;
    }

    .feature-strip {
        display: flex;
        justify-content: center;
        gap: 2.2rem;
        margin-top: 2.2rem;
        margin-bottom: 1.8rem;
        opacity: 0;
        animation: fadeInUp 0.9s ease forwards;
        animation-delay: 2.6s;
    }
    .feature-item {
        text-align: center;
        max-width: 140px;
    }
    .feature-icon {
        font-size: 1.6rem;
        margin-bottom: 0.4rem;
    }
    .feature-label {
        font-size: 0.85rem;
        font-weight: 600;
        color: #d8d8d8;
    }

    .cta-section {
        text-align: center;
        margin-bottom: 1.6rem;
        opacity: 0;
        animation: fadeInUp 0.9s ease forwards;
        animation-delay: 3.1s;
    }
    .cta-section .stButton>button {
        border-radius: 30px !important;
        background: linear-gradient(90deg, rgba(255,106,106,0.18), rgba(255,184,108,0.18)) !important;
        border: 1px solid rgba(255, 138, 92, 0.4) !important;
        color: #ffb86c !important;
        font-weight: 700 !important;
        padding: 0.5rem 1.4rem !important;
        animation: pulseGlow 2.5s infinite;
        width: auto !important;
    }
    .cta-section .stButton>button:hover {
        transform: translateY(-2px);
    }

    .input-wrap {
        opacity: 0;
        animation: fadeInUp 0.9s ease forwards;
        animation-delay: 3.6s;
        position: relative;
        z-index: 1;
    }

    .stButton>button {
        border-radius: 10px;
        font-weight: 700;
        font-size: 1.05rem;
        padding: 0.85rem 1.5rem;
        background: linear-gradient(90deg, #ff6a6a, #ffb86c);
        border: none;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 22px rgba(255, 106, 106, 0.4);
    }

    .section-title {
        font-family: 'Poppins', sans-serif;
        font-weight: 700;
        font-size: 1.3rem;
        margin-top: 2.4rem;
        margin-bottom: 1rem;
    }

    .card-grid {
        display: flex;
        flex-direction: column;
        gap: 0.9rem;
    }
    .suggestion-card {
        background: linear-gradient(145deg, rgba(255, 106, 106, 0.06), rgba(255, 184, 108, 0.04));
        border: 1px solid rgba(255, 138, 92, 0.18);
        border-radius: 16px;
        padding: 1.6rem 1.8rem;
        display: flex;
        flex-direction: column;
        gap: 0.7rem;
        transition: all 0.25s ease;
        animation: cardFadeIn 0.5s ease forwards;
        opacity: 0;
    }
    .suggestion-card:hover {
        border-color: rgba(255, 138, 92, 0.55);
        background: linear-gradient(145deg, rgba(255, 106, 106, 0.1), rgba(255, 184, 108, 0.07));
        transform: translateY(-3px);
        box-shadow: 0 12px 28px rgba(255, 106, 106, 0.15);
    }
    .card-top-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .suggestion-title {
        font-size: 1.2rem;
        font-weight: 700;
    }
    .difficulty-pill {
        font-size: 0.85rem;
        font-weight: 700;
        padding: 0.3rem 0.9rem;
        border-radius: 20px;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }
    .difficulty-easy { background: rgba(74, 222, 128, 0.15); color: #4ade80; }
    .difficulty-medium { background: rgba(250, 204, 21, 0.15); color: #facc15; }
    .difficulty-hard { background: rgba(248, 113, 113, 0.15); color: #f87171; }

    .suggestion-reason {
        color: #c8c8c8;
        font-size: 1.02rem;
        line-height: 1.6;
    }
    .suggestion-card a {
        color: #ffb86c;
        font-weight: 600;
        font-size: 0.9rem;
        text-decoration: none;
    }
    .suggestion-card a:hover {
        text-decoration: underline;
    }

    .tech-badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 6px;
        padding: 0.25rem 0.7rem;
        margin: 0.2rem 0.3rem 0.2rem 0;
        font-size: 0.88rem;
    }
</style>
""", unsafe_allow_html=True)

# ---------- Sparkle Background ----------
sparkle_positions = [
    ("6%", "12%", "0s"), ("92%", "18%", "0.6s"), ("15%", "35%", "1.2s"),
    ("85%", "42%", "0.3s"), ("8%", "60%", "0.9s"), ("90%", "65%", "1.5s"),
]
sparkles_html = "".join(
    f'<div class="sparkle" style="top:{top}; left:{left}; animation-delay:{delay};">✦</div>'
    for top, left, delay in sparkle_positions
)
st.markdown(sparkles_html, unsafe_allow_html=True)

# ---------- Header (with GitHub icons on both sides) ----------
GITHUB_SVG = """<svg class="github-icon" viewBox="0 0 16 16" fill="#ffb86c" xmlns="http://www.w3.org/2000/svg">
<path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38
0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01
1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95
0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27
2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82
1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48
0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0016 8c0-4.42-3.58-8-8-8z"/>
</svg>"""

st.markdown(f"""
<div class="header-wrap">
    <div class="title-row">
        {GITHUB_SVG}
        <div class="main-title">Welcome to AI RepoGuide</div>
        {GITHUB_SVG}
    </div>
    <p class="subtitle">Your AI-powered guide to make meaningful open-source contributions.
    Understand any repo in seconds, and level up from first-timer to confident contributor.</p>
</div>
""", unsafe_allow_html=True)

# ---------- Feature Strip ----------
st.markdown("""
<div class="feature-strip">
    <div class="feature-item">
        <div class="feature-icon">🔍</div>
        <div class="feature-label">Understand the repo</div>
    </div>
    <div class="feature-item">
        <div class="feature-icon">🎯</div>
        <div class="feature-label">Discover good issues</div>
    </div>
    <div class="feature-item">
        <div class="feature-icon">🚀</div>
        <div class="feature-label">Start contributing</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------- CTA Button (triggers confetti) ----------
st.markdown('<div class="cta-section">', unsafe_allow_html=True)
col_l, col_mid, col_r = st.columns([1, 1, 1])
with col_mid:
    if st.button("🎉 Let's Start Contributing!", key="cta_button"):
        st.session_state.show_confetti = True
st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.show_confetti:
    components.html("""
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.9.2/dist/confetti.browser.min.js"></script>
    <script>
        confetti({
            particleCount: 150,
            spread: 100,
            origin: { y: 0.4 },
            colors: ['#ff6a6a', '#ffb86c', '#4ade80', '#facc15', '#ffffff']
        });
        setTimeout(function() {
            confetti({ particleCount: 80, angle: 60, spread: 70, origin: { x: 0 } });
            confetti({ particleCount: 80, angle: 120, spread: 70, origin: { x: 1 } });
        }, 250);
    </script>
    """, height=0, width=0)
    st.session_state.show_confetti = False

# ---------- Input Card ----------
st.markdown('<div class="input-wrap">', unsafe_allow_html=True)
with st.container(border=True):
    repo_url = st.text_input("GitHub repo URL", placeholder="https://github.com/owner/repo")

    with st.expander("Tell us about yourself (optional, improves suggestions)"):
        col1, col2 = st.columns(2)
        with col1:
            skill_level = st.selectbox("Experience level", ["Beginner", "Intermediate", "Advanced"])
        with col2:
            languages_known = st.text_input("Languages you know", placeholder="Python, JavaScript")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div style='margin-top: 1.8rem;'></div>", unsafe_allow_html=True)
analyze_btn = st.button("Analyze Repo", type="primary", use_container_width=True)

# ---------- Results ----------
if analyze_btn:
    if not repo_url.strip():
        st.warning("Please paste a GitHub repo URL first.")
    else:
        try:
            with st.spinner("Fetching repo data from GitHub..."):
                repo_data = fetch_repo_data(repo_url)

            user_profile = f"{skill_level}, knows: {languages_known or 'not specified'}"

            with st.spinner("Analyzing with AI..."):
                result = analyze_repo(repo_data, user_profile)

            st.success(f"Analysis complete for **{repo_data['name']}** ⭐ {repo_data['stars']}")

            st.markdown('<div class="section-title">What is this project?</div>', unsafe_allow_html=True)
            st.write(result["summary"])

            st.markdown('<div class="section-title">Tech Stack</div>', unsafe_allow_html=True)
            badges_html = "".join(f'<span class="tech-badge">{t}</span>' for t in result["tech_stack"])
            st.markdown(badges_html, unsafe_allow_html=True)

            st.markdown('<div class="section-title">Suggested First Contributions</div>', unsafe_allow_html=True)
            difficulty_class = {"easy": "difficulty-easy", "medium": "difficulty-medium", "hard": "difficulty-hard"}

            card_parts = ['<div class="card-grid">']
            for i, s in enumerate(result["suggestions"]):
                cls = difficulty_class.get(s["difficulty"].lower(), "")
                issue_link = f'<a href="{s["issue_url"]}" target="_blank">View issue →</a>' if s.get("issue_url") else ""
                delay = f"animation-delay: {i * 0.12}s;"
                card_html = (
                    f'<div class="suggestion-card" style="{delay}">'
                    f'<div class="card-top-row">'
                    f'<div class="suggestion-title">{s["title"]}</div>'
                    f'<span class="difficulty-pill {cls}">{s["difficulty"]}</span>'
                    f'</div>'
                    f'<div class="suggestion-reason">{s["reason"]}</div>'
                    f'{issue_link}'
                    f'</div>'
                )
                card_parts.append(card_html)
            card_parts.append('</div>')
            st.markdown("".join(card_parts), unsafe_allow_html=True)

        except ValueError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"Something went wrong: {e}")