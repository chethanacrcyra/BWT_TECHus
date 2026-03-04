import streamlit as st
import pandas as pd
import base64

st.set_page_config(page_title="NeuroDrive DNA – AI Productivity Analyzer", layout="wide")

if "sessions" not in st.session_state:
    st.session_state.sessions = []
if "modules" not in st.session_state:
    st.session_state.modules = {}
if "username" not in st.session_state:
    st.session_state.username = ""
if "email" not in st.session_state:
    st.session_state.email = ""

st.sidebar.title("NeuroDrive DNA")
page = st.sidebar.radio(
    "Navigation",
    ["Credentials", "Course & Modules", "Personal Dashboard"]
)

st.title("🧠 NeuroDrive DNA – AI Productivity Analyzer")

if page == "Credentials":
    st.header("🔐 User Credentials")
    col1, col2 = st.columns(2)
    with col1:
        username = st.text_input("Username", value=st.session_state.username)
        email = st.text_input("Email ID", value=st.session_state.email)
        if st.button("Save Credentials"):
            if username.strip() and email.strip() and ("@" in email):
                st.session_state.username = username.strip()
                st.session_state.email = email.strip()
                st.success("Credentials saved successfully")
            else:
                st.warning("Please enter a username and a valid email address.")
    with col2:
        st.subheader("Current Profile")
        st.write(f"Username: {st.session_state.username or '—'}")
        st.write(f"Email: {st.session_state.email or '—'}")

elif page == "Course & Modules":
    st.header("📚 Course and Module Manager")
    left, right = st.columns([2, 1])
    with left:
        course = st.text_input("Course Name")
        module = st.text_input("Module Name")
        duration = st.number_input("Focus Duration (minutes)", min_value=1, step=5, value=25)
        if module:
            uploaded_pdf = st.file_uploader("Upload Module PDF", type=["pdf"])
            if uploaded_pdf is not None:
                st.session_state.modules[module] = uploaded_pdf.name
                st.success(f"Uploaded PDF for module: {module}")
                pdf_bytes = uploaded_pdf.getvalue()
                base64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
                pdf_display = f"""
                <iframe src="data:application/pdf;base64,{base64_pdf}"
                width="700" height="500" type="application/pdf"></iframe>
                """
                st.markdown(pdf_display, unsafe_allow_html=True)
        if st.button("Add Focus Session"):
            if course.strip() and module.strip() and duration > 0:
                st.session_state.sessions.append({
                    "course": course.strip(),
                    "module": module.strip(),
                    "duration": float(duration),
                })
                st.success("Focus session recorded!")
            else:
                st.warning("Please enter course, module, and a positive duration.")
        st.subheader("Focus Sessions")
        df = pd.DataFrame(st.session_state.sessions)
        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No focus sessions yet.")
    with right:
        st.subheader("Uploaded Modules")
        if st.session_state.modules:
            for m, file in st.session_state.modules.items():
                st.write(f"📄 {m} → {file}")
        else:
            st.caption("No modules uploaded yet.")

elif page == "Personal Dashboard":
    st.header("📈 Personal Productivity Dashboard")
    info1, info2 = st.columns(2)
    with info1:
        st.write(f"Username: {st.session_state.username or '—'}")
    with info2:
        st.write(f"Email: {st.session_state.email or '—'}")
    total_sessions = len(st.session_state.sessions)
    total_modules = len(st.session_state.modules)
    durations = [s["duration"] for s in st.session_state.sessions] if total_sessions else []
    total_duration = sum(durations) if durations else 0.0
    avg_focus = (total_duration / total_sessions) if total_sessions else 0.0
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Focus Sessions", total_sessions)
    m2.metric("Average Focus Duration", f"{avg_focus:.1f} min")
    m3.metric("Total Uploaded Modules", total_modules)
    st.subheader("🧬 Distraction DNA Analysis")
    if total_sessions == 0:
        st.info("No productivity data available yet.")
    else:
        if avg_focus < 10:
            dna = "🧬 Quick Distractor"
            msg = "Your focus sessions are short. Try 20-minute focus blocks."
            st.warning(f"{dna} • Average: {avg_focus:.1f} min")
        elif 10 <= avg_focus < 25:
            dna = "🧬 Balanced Learner"
            msg = "You maintain moderate focus. Increase session length gradually."
            st.info(f"{dna} • Average: {avg_focus:.1f} min")
        else:
            dna = "🧬 Deep Focus Achiever"
            msg = "Excellent concentration. Maintain your deep focus habits."
            st.success(f"{dna} • Average: {avg_focus:.1f} min")
        st.write(msg)
    st.subheader("📊 Productivity Trend")
    if total_sessions:
        chart_df = pd.DataFrame({"Focus Duration (min)": durations})
        st.line_chart(chart_df, use_container_width=True)
    else:
        st.info("No productivity data available yet.")