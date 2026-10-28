from pathlib import Path
import json
import joblib
import pandas as pd
import streamlit as st
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
MODEL_PATH = ROOT / "models" / "risk_model.joblib"
DATA_PATH = ROOT / "data" / "activity_data.csv"
METRICS_PATH = ROOT / "reports" / "metrics.json"

st.set_page_config(page_title="MindShield AI | Child Safety", page_icon="🛡️", layout="wide", initial_sidebar_state="expanded")

FEATURES = ["screen_time_hours", "late_night_hours", "blocked_site_attempts", "unknown_contact_attempts", "rapid_app_switches", "sleep_hours", "educational_usage_pct", "weekend"]
DEFAULT_BLOCKLIST = {
    "adult-example.test": "18+ content (demo entry)",
    "unsafe-example.test": "Unsafe content (demo entry)",
    "scam-example.test": "Suspicious / scam (demo entry)",
}

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
:root{--bg:#08111f;--card:#111f33;--line:rgba(148,163,184,.18);--teal:#42e0c4;--blue:#69aaff;--text:#eff6ff;--muted:#9eb0c9}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif}.stApp{background:radial-gradient(ellipse at 10% 0%,rgba(20,130,145,.2),transparent 35%),radial-gradient(ellipse at 90% 5%,rgba(74,84,180,.18),transparent 30%),var(--bg);color:var(--text)}
.block-container{max-width:1450px;padding-top:1.4rem;padding-bottom:3rem}[data-testid="stSidebar"]{background:#0d192a;border-right:1px solid var(--line)}
[data-testid="stMetric"]{background:linear-gradient(145deg,#152943,#101c2e);border:1px solid var(--line);border-radius:16px;padding:15px 18px}[data-testid="stMetricLabel"]{color:var(--muted)!important}[data-testid="stMetricValue"]{color:#f5f9ff!important;font-family:'Manrope',sans-serif}
.stButton>button,.stDownloadButton>button{border-radius:11px;font-weight:700;border:1px solid rgba(66,224,196,.35)}.stButton>button[kind="primary"]{background:linear-gradient(100deg,#20c9b6,#3d8cf4);color:#061321;border:0}
[data-testid="stTabs"] button{font-weight:700;padding:12px 14px}[data-testid="stTabs"] button[aria-selected="true"]{color:var(--teal)!important;border-bottom-color:var(--teal)!important}
.hero{border:1px solid rgba(105,170,255,.25);border-radius:24px;padding:28px 30px;background:linear-gradient(115deg,#15344a,#20244c 62%,#10433f);margin-bottom:18px;position:relative;overflow:hidden}.eyebrow{color:var(--teal);font-size:11px;font-weight:800;letter-spacing:2px}.title{font-family:'Manrope',sans-serif;font-size:clamp(30px,4vw,46px);font-weight:800;margin:7px 0}.sub{color:#c3d4e9;font-size:16px;max-width:850px}.chip{display:inline-block;margin:12px 6px 0 0;padding:6px 10px;border-radius:30px;background:rgba(66,224,196,.12);border:1px solid rgba(66,224,196,.25);color:#8af0e1;font-size:12px}.panel{background:linear-gradient(145deg,#14243a,#101b2d);border:1px solid var(--line);border-radius:17px;padding:18px 20px}.section{font-family:'Manrope',sans-serif;font-size:23px;font-weight:800;margin:8px 0 4px}.muted{color:var(--muted);font-size:14px}.status-good{color:#71edb6;font-weight:800}.status-warn{color:#ffd166;font-weight:800}.status-bad{color:#ff8585;font-weight:800}.stAlert{border-radius:12px}footer{visibility:hidden}
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_bundle():
    return joblib.load(MODEL_PATH) if MODEL_PATH.exists() else None
@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH) if DATA_PATH.exists() else pd.DataFrame()
@st.cache_data
def load_metrics():
    if METRICS_PATH.exists():
        with open(METRICS_PATH, encoding="utf-8") as f: return json.load(f)
    return {}

def normalize_domain(raw):
    raw = raw.strip()
    if not raw: return ""
    parsed = urlparse(raw if "://" in raw else "https://" + raw)
    host = (parsed.hostname or "").lower().strip(".")
    return host.removeprefix("www.")

def match_blocklist(domain, blocklist):
    for blocked_domain, category in blocklist.items():
        blocked_domain = blocked_domain.lower().strip().lstrip(".")
        if domain == blocked_domain or domain.endswith("." + blocked_domain):
            return category
    return None

if "custom_blocklist" not in st.session_state:
    st.session_state.custom_blocklist = DEFAULT_BLOCKLIST.copy()
if "blocked_attempts" not in st.session_state:
    st.session_state.blocked_attempts = 0
if "checked_sites" not in st.session_state:
    st.session_state.checked_sites = 0

st.markdown("""
<div class="hero"><div class="eyebrow">CHILD ONLINE PROTECTION · DIGITAL WELLBEING</div>
<div class="title">🛡️ MindShield AI</div>
<div class="sub">A child-first safety dashboard concept that helps caregivers review website blocklists, identify demo-listed risky domains, and build healthier screen-time routines.</div>
<span class="chip">🌐 Website safety checker</span><span class="chip">🔒 18+ blocklist concept</span><span class="chip">🌿 Digital wellbeing</span><span class="chip">🧠 ML learning lab</span></div>
""", unsafe_allow_html=True)
st.warning("PROTOTYPE LIMITATION: This Streamlit app checks domains against a local demo blocklist. It does NOT automatically block websites in Chrome or other browsers, scan all internet content, or guarantee that a website is safe. Real device-level blocking requires a managed DNS filter, parental-control service, or browser extension and a maintained age-inappropriate-domain feed.")

with st.sidebar:
    st.markdown("## 🛡️ Protection settings")
    st.caption("Configure this demonstration's local domain list.")
    st.metric("Domains in demo blocklist", len(st.session_state.custom_blocklist))
    st.metric("Blocked demo attempts", st.session_state.blocked_attempts)
    st.metric("Website checks", st.session_state.checked_sites)
    st.markdown("---")
    st.markdown("**Protection mode**")
    st.info("Demo mode · Checks only when a URL is submitted here")
    st.caption("For real child protection, configure filtering on the child's device/router and protect settings with a caregiver PIN.")

tabs = st.tabs(["🛡️ Protection center", "🌐 Website checker", "🌿 Digital wellbeing", "🧠 ML lab", "⚙️ Setup & limitations", "🧒 Child safe home"])

with tabs[0]:
    st.markdown('<div class="section">Your protection overview</div>', unsafe_allow_html=True)
    st.markdown('<div class="muted">A simple, caregiver-friendly view of the key safety and wellbeing tools.</div>', unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Demo blocklist", f"{len(st.session_state.custom_blocklist)} domains", "editable list")
    c2.metric("Checks performed", st.session_state.checked_sites, "this session")
    c3.metric("Blocked matches", st.session_state.blocked_attempts, "demo checks only")
    c4.metric("Wellbeing goal", "2 hours", "customizable leisure target")
    st.markdown("### Quick actions")
    a,b,c = st.columns(3)
    with a:
        st.markdown('<div class="panel"><h4>🌐 Check a website</h4><p>Compare a domain with the local demo blocklist before opening it.</p></div>',unsafe_allow_html=True)
        if st.button("Open website checker", use_container_width=True): st.session_state.active_action="checker"
    with b:
        st.markdown('<div class="panel"><h4>🚧 Manage blocked domains</h4><p>Add a domain to the local blocklist for this running session.</p></div>',unsafe_allow_html=True)
        if st.button("Manage demo list", use_container_width=True): st.session_state.active_action="blocklist"
    with c:
        st.markdown('<div class="panel"><h4>🌿 Build healthy habits</h4><p>Set a screen-time goal and plan breaks, sleep, and learning time.</p></div>',unsafe_allow_html=True)
        if st.button("Open wellbeing planner", use_container_width=True): st.session_state.active_action="wellbeing"
    if st.session_state.get("active_action") == "checker": st.info("Select the Website checker tab above to check a domain.")
    elif st.session_state.get("active_action") == "blocklist": st.info("Select the Website checker tab to add or remove demo blocklist entries.")
    elif st.session_state.get("active_action") == "wellbeing": st.info("Select the Digital wellbeing tab to customize routines.")
    st.markdown("### How protection is intended to work")
    st.markdown("**1. Identify** a domain using a maintained category/blocklist source.  **2. Decide** whether to allow or block it under caregiver rules.  **3. Enforce** the rule through DNS, a browser extension, or device parental controls.  **4. Review** transparent, minimal logs and wellbeing trends with the child.")
    st.caption("The current college prototype implements the local checking and wellbeing-planning interface. It does not enforce network-level rules.")

with tabs[1]:
    st.markdown('<div class="section">Website safety checker</div>', unsafe_allow_html=True)
    st.markdown('<div class="muted">Check a domain against the demo blocklist. A result of “not listed” does not mean the website is safe.</div>', unsafe_allow_html=True)
    url = st.text_input("Enter a website URL or domain", placeholder="https://example.com", help="Avoid entering personal details or private browsing history.")
    if st.button("🔎 Check website", type="primary"):
        domain = normalize_domain(url)
        if not domain or "." not in domain or " " in domain:
            st.error("Please enter a valid-looking domain, such as example.com.")
        else:
            st.session_state.checked_sites += 1
            category = match_blocklist(domain, st.session_state.custom_blocklist)
            if category:
                st.session_state.blocked_attempts += 1
                st.error(f"⛔ DEMO BLOCK MATCH — {domain}")
                st.markdown(f'<div class="panel"><div class="status-bad">BLOCKLIST MATCH</div><h3>Do not open in this demo</h3><p>Category: {category}</p><p>This is a match in the local list, not a live network block.</p></div>',unsafe_allow_html=True)
            else:
                st.warning(f"⚠️ {domain} is not in this demo blocklist. This is NOT a safety certification.")
                st.markdown('<div class="panel"><div class="status-warn">NOT VERIFIED</div><p>Use a trusted safe-browsing or parental-control service to assess the domain. This prototype does not crawl or inspect website content.</p></div>',unsafe_allow_html=True)
    st.markdown("### Demo blocklist manager")
    with st.form("add_domain_form", clear_on_submit=True):
        new_domain = st.text_input("Domain to add", placeholder="unwanted-example.test")
        category = st.selectbox("Reason/category", ["18+ content (caregiver-defined)", "Unsafe content (caregiver-defined)", "Scam / suspicious (caregiver-defined)", "Other caregiver-defined rule"])
        add = st.form_submit_button("＋ Add to demo blocklist")
        if add:
            domain = normalize_domain(new_domain)
            if not domain or "." not in domain or " " in domain:
                st.error("Enter a valid-looking domain.")
            else:
                st.session_state.custom_blocklist[domain] = category
                st.success(f"Added {domain} to the local demo list.")
    if st.session_state.custom_blocklist:
        list_df = pd.DataFrame([{"Domain": d, "Caregiver-defined category": c} for d,c in sorted(st.session_state.custom_blocklist.items())])
        st.dataframe(list_df, use_container_width=True, hide_index=True)
        csv = list_df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download blocklist CSV", csv, "mindshield_demo_blocklist.csv", "text/csv")
        remove_domain = st.selectbox("Select a domain to remove", ["— select —"] + sorted(st.session_state.custom_blocklist.keys()))
        if st.button("Remove selected domain"):
            if remove_domain != "— select —":
                del st.session_state.custom_blocklist[remove_domain]
                st.rerun()
    st.info("The included domains ending in .test are illustrative placeholders, not real websites. Add domains that are appropriate for your demonstration. A real product needs a reputable, regularly updated category feed and a reliable enforcement layer.")

with tabs[2]:
    st.markdown('<div class="section">Digital wellbeing planner</div>', unsafe_allow_html=True)
    st.markdown('<div class="muted">Create a balanced routine. Goals are adjustable and should fit the child’s age, school schedule, and family needs.</div>', unsafe_allow_html=True)
    l,r = st.columns(2)
    with l:
        st.markdown("#### 📱 Screen-time routine")
        leisure_goal = st.slider("Daily recreational screen-time goal (hours)", 0.5, 8.0, 2.0, 0.5)
        actual_screen = st.slider("Sample recreational screen time today (hours)", 0.0, 12.0, 3.0, 0.5)
        break_interval = st.selectbox("Take a movement / eye break every", [20, 30, 45, 60], index=1, format_func=lambda x: f"{x} minutes")
        learning_hours = st.slider("Learning / creative screen time (hours)", 0.0, 8.0, 1.5, 0.5)
    with r:
        st.markdown("#### 😴 Rest and healthy habits")
        sleep_goal = st.slider("Target sleep (hours)", 7.0, 12.0, 9.0, 0.5)
        actual_sleep = st.slider("Sample sleep last night (hours)", 3.0, 12.0, 8.0, 0.5)
        no_screen_before_bed = st.checkbox("Plan a screen-free wind-down before bed", value=True)
        family_checkin = st.checkbox("Plan a supportive family check-in", value=True)
    st.markdown("### Today’s gentle check-in")
    m1,m2,m3 = st.columns(3)
    m1.metric("Recreational screen time", f"{actual_screen:g} h", f"{actual_screen-leisure_goal:+.1f} h vs goal")
    m2.metric("Sleep", f"{actual_sleep:g} h", f"{actual_sleep-sleep_goal:+.1f} h vs target")
    m3.metric("Learning / creative use", f"{learning_hours:g} h", "positive-purpose screen time")
    if actual_screen <= leisure_goal: st.success("Recreational screen-time sample is within your chosen goal. Keep balancing online and offline activities.")
    else: st.info("The sample is above your chosen recreational screen-time goal. Consider a collaborative plan for breaks and offline activities—avoid blame or punishment.")
    suggestions=[]
    if actual_sleep < sleep_goal: suggestions.append("Try a consistent bedtime routine and protect enough time for sleep.")
    if no_screen_before_bed: suggestions.append("Keep the chosen screen-free wind-down period calm and realistic.")
    if family_checkin: suggestions.append("Ask what felt positive or uncomfortable online, listen without judgment, and agree on next steps together.")
    suggestions.append(f"Schedule a short movement/eye break about every {break_interval} minutes during long sessions.")
    for s in suggestions: st.markdown(f"- {s}")
    st.caption("These are general wellbeing prompts, not medical advice. Needs vary by age and individual circumstances.")

with tabs[3]:
    st.markdown('<div class="section">Machine-learning lab</div>', unsafe_allow_html=True)
    st.markdown('<div class="muted">The ML model is a supporting classroom experiment—not the mechanism that blocks websites.</div>', unsafe_allow_html=True)
    bundle = load_bundle(); data = load_data(); metrics = load_metrics()
    if bundle:
        model = bundle["model"]
        with st.expander("Run an illustrative digital-habit classification"):
            c1,c2,c3 = st.columns(3)
            screen = c1.slider("Screen time (h)",0.0,14.0,4.0,0.5,key="ml_screen")
            late = c2.slider("Late-night use (h)",0.0,8.0,1.0,0.5,key="ml_late")
            sleep = c3.slider("Sleep (h)",3.0,12.0,8.0,0.5,key="ml_sleep")
            edu = c1.slider("Educational use (%)",0,100,50,5,key="ml_edu")
            blocked = c2.number_input("Blocked-site attempts",0,15,1,key="ml_blocked")
            unknown = c3.number_input("Unknown-contact attempts",0,12,0,key="ml_unknown")
            switches = st.slider("Rapid app switches",0,70,18,key="ml_switches")
            weekend = st.selectbox("Day type",["Weekday","Weekend"],key="ml_weekend")
            if st.button("Assess sample habits",type="primary"):
                sample = pd.DataFrame([{"screen_time_hours":screen,"late_night_hours":late,"blocked_site_attempts":blocked,"unknown_contact_attempts":unknown,"rapid_app_switches":switches,"sleep_hours":sleep,"educational_usage_pct":edu,"weekend":1 if weekend=="Weekend" else 0}],columns=FEATURES)
                pred = str(model.predict(sample)[0]); probs=model.predict_proba(sample)[0]; classes=list(model.classes_)
                st.metric("Illustrative model category",pred)
                st.bar_chart(pd.DataFrame({"Model probability":probs},index=classes))
                st.caption("Probabilities refer only to the model's synthetic training labels. They are not probabilities of a child being safe or unsafe.")
    if metrics:
        x,y,z=st.columns(3); x.metric("Synthetic-label test accuracy",f"{metrics.get('accuracy',0):.1%}"); y.metric("Macro F1",f"{metrics.get('macro_f1',0):.3f}"); z.metric("Test rows",metrics.get("test_rows",0))
        st.caption("Metrics measure reproduction of simulated labels, not real-world safety or content-filter accuracy.")
    if not data.empty:
        with st.expander("Explore simulated training dataset"):
            st.dataframe(data.head(25),use_container_width=True,hide_index=True)
            st.download_button("Download simulated dataset",data.to_csv(index=False).encode(),"mindshield_simulated_activity_data.csv","text/csv")

with tabs[4]:
    st.markdown('<div class="section">How to make this real protection</div>', unsafe_allow_html=True)
    st.markdown("### Current prototype vs. a deployable safety product")
    st.markdown("**Implemented here:** local demo blocklist matching, caregiver-managed demo entries, CSV export, wellbeing goal planner, and an optional synthetic-data ML lab.\n\n**Not implemented:** browser/network interception, reliable detection of all 18+ sites, bypass prevention, user accounts/PIN, live alerts, or real device usage tracking.")
    st.markdown("### Recommended architecture for the next version")
    st.markdown("1. **Filtering layer:** integrate a reputable family-safe DNS filtering service or build a browser extension that checks navigation before a page loads.\n2. **Category source:** use a licensed/reputable, regularly updated adult-content and malware/phishing category feed. Avoid relying only on keywords.\n3. **Caregiver controls:** authenticated parent account, PIN-protected settings, allowlist/denylist, age-appropriate policies, and transparent explanations.\n4. **Wellbeing:** opt-in screen-time summaries, break reminders, bedtime schedules, and collaborative family goals.\n5. **Privacy and safety:** collect the minimum data, secure logs, define retention, provide an override for emergencies, and test false positives/negatives.")
    st.warning("A Streamlit app hosted on the cloud cannot, by itself, control a child’s local browser or Wi-Fi traffic. To actually prevent access, the filtering component must run in the browser, on the device, or at the network/DNS level.")
    st.markdown("### Technology stack")
    st.write("Python · Streamlit · Pandas · Scikit-learn · Joblib · Local domain-list prototype")

with tabs[5]:
    st.markdown('<div class="section">🧒 My Safe Space</div>', unsafe_allow_html=True)
    st.markdown('<div class="muted">A child-friendly home screen for safe browsing and balanced screen time.</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="hero">
      <div class="eyebrow">WELCOME TO YOUR SAFE SPACE</div>
      <div class="title">Explore. Learn. Take breaks. 🌈</div>
      <div class="sub">Find learning ideas, check a website with your caregiver’s safety rules, and remember to make time for offline fun.</div>
      <span class="chip">📚 Learn something new</span><span class="chip">🛡️ Safer browsing</span><span class="chip">🌿 Healthy habits</span>
    </div>
    """, unsafe_allow_html=True)
    st.info("This is a demonstration portal. It does not replace a browser filter and does not monitor activity in other apps or websites.")
    left, right = st.columns([1.4, 1])
    with left:
        st.markdown("### 🔎 Check before visiting")
        child_url = st.text_input("Website or domain", placeholder="Type a domain, e.g. example.com", key="child_domain")
        if st.button("Check website safety", type="primary", use_container_width=True, key="child_check"):
            child_domain = normalize_domain(child_url)
            if not child_domain or "." not in child_domain or " " in child_domain:
                st.error("Please enter a valid domain, such as example.com.")
            else:
                st.session_state.checked_sites += 1
                child_category = match_blocklist(child_domain, st.session_state.custom_blocklist)
                if child_category:
                    st.session_state.blocked_attempts += 1
                    st.session_state.child_last_result = (child_domain, child_category, True)
                else:
                    st.session_state.child_last_result = (child_domain, "Not listed in the demo blocklist", False)
        result = st.session_state.get("child_last_result")
        if result:
            domain, category, blocked = result
            if blocked:
                st.error(f"⛔ This demo blocks {domain}")
                st.markdown(f'<div class="panel"><div class="status-bad">SAFETY RULE MATCH</div><h3>Let’s choose another activity.</h3><p>Reason: {category}</p><p>Ask a trusted adult if you think this is a mistake.</p></div>', unsafe_allow_html=True)
            else:
                st.warning(f"{domain} is not on this demo list. That does not mean it is safe.")
                st.markdown('<div class="panel"><div class="status-warn">CAREGIVER CHECK NEEDED</div><p>This prototype cannot verify the full website. Ask a caregiver before visiting unfamiliar sites.</p></div>', unsafe_allow_html=True)
    with right:
        st.markdown("### ⏱️ Screen-time agreement")
        daily_limit = st.select_slider("Daily recreational screen-time goal", options=[15, 20, 30, 45, 60], value=30, format_func=lambda x: f"{x} minutes")
        used_minutes = st.number_input("Demo minutes used today", min_value=0, max_value=600, value=0, step=5, help="Enter a sample value for the college demonstration; this is not tracked automatically.")
        remaining = max(0, daily_limit - used_minutes)
        st.metric("Time remaining in demo goal", f"{remaining} min", "Goal reached" if remaining == 0 else "Take breaks too")
        st.progress(min(1.0, used_minutes / daily_limit))
        if remaining == 0:
            st.warning("Your selected screen-time goal has been reached. Pause browsing and choose an offline activity.")
        else:
            st.success("You are within the selected demo goal. Remember to stretch and rest your eyes.")
    st.markdown("### 🌟 Try an offline break")
    cards = st.columns(3)
    for col, emoji, title, desc in [
        (cards[0], "📖", "Read a story", "Spend 10 minutes with a book."),
        (cards[1], "⚽", "Move your body", "Play outside, stretch, or dance."),
        (cards[2], "🎨", "Make something", "Draw, build, or try a small craft.")]:
        with col:
            st.markdown(f'<div class="panel"><h3>{emoji} {title}</h3><p>{desc}</p></div>', unsafe_allow_html=True)
    st.caption("For real enforcement of adult-site blocking or a 30-minute limit, install and configure a trusted browser extension, device parental controls, or family-safe DNS filtering on the child’s device. This page only demonstrates the intended experience.")

st.markdown('<hr style="border-color:rgba(148,163,184,.18)"><p style="text-align:center;color:#9eb0c9;font-size:13px">M I N D S H I E L D  A I · Protect with care. Build healthy digital habits.</p>',unsafe_allow_html=True)
