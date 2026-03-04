import streamlit as st
import pandas as pd
import base64

st.set_page_config(page_title="NeuroDrive DNA – AI Productivity Analyzer", layout="wide")

# ---------------------------
# Session State Initialization
# ---------------------------

if "sessions" not in st.session_state:
    st.session_state.sessions = []

if "modules" not in st.session_state:
    st.session_state.modules = {}

if "username" not in st.session_state:
    st.session_state.username = ""

if "email" not in st.session_state:
    st.session_state.email = ""

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "page" not in st.session_state:
    st.session_state.page = "Credentials"
if "modules_by_course" not in st.session_state:
    st.session_state.modules_by_course = {}
if "selected_course" not in st.session_state:
    st.session_state.selected_course = None
if "selected_module" not in st.session_state:
    st.session_state.selected_module = None

# ---------------------------
# Sidebar Navigation
# ---------------------------

st.sidebar.title("NeuroDrive DNA")

pages = ["Credentials", "Course & Modules", "Personal Dashboard"]

selected_page = st.sidebar.radio(
    "Navigation",
    pages,
    index=pages.index(st.session_state.page)
)

st.session_state.page = selected_page

st.title("🧠 NeuroDrive DNA – AI Productivity Analyzer")

# ---------------------------
# Credentials Page
# ---------------------------

if st.session_state.page == "Credentials":

    st.header("🔐 User Credentials")

    col1, col2 = st.columns(2)

    with col1:
        username = st.text_input("Username", value=st.session_state.username)
        email = st.text_input("Email ID", value=st.session_state.email)
        password = st.text_input("Password", type="password")

        if st.button("Login"):

            if username.strip() and email.strip() and ("@" in email) and password.strip():

                st.session_state.username = username.strip()
                st.session_state.email = email.strip()
                st.session_state.logged_in = True

                st.session_state.page = "Course & Modules"

                st.success("Login successful! Redirecting...")
                st.rerun()

            else:
                st.warning("Enter username, valid email, and password.")

    with col2:

        st.subheader("Current Profile")

        st.write(f"Username: {st.session_state.username or '—'}")
        st.write(f"Email: {st.session_state.email or '—'}")

# ---------------------------
# Course & Modules Page
# ---------------------------

elif st.session_state.page == "Course & Modules":

    st.header("📚 Course and Module Manager")

    left, right = st.columns([2, 1])

    with left:
        course = st.text_input("Course Name")
        module = st.text_input("Module Name")

        uploaded_pdf = None
        if module and course:
            uploaded_pdf = st.file_uploader("Upload Module PDF", type=["pdf"])
            if uploaded_pdf is not None:
                file_bytes = uploaded_pdf.getvalue()
                b64 = base64.b64encode(file_bytes).decode("utf-8")
                if course not in st.session_state.modules_by_course:
                    st.session_state.modules_by_course[course] = {}
                st.session_state.modules_by_course[course][module] = {
                    "file_name": uploaded_pdf.name,
                    "base64": b64,
                }
                st.success(f"Uploaded PDF for module: {module}")
                st.markdown(
                    f"""
                    <iframe src="data:application/pdf;base64,{b64}"
                    width="700" height="500" type="application/pdf"></iframe>
                    """,
                    unsafe_allow_html=True
                )
        elif module and not course:
            st.info("Enter Course Name before uploading a module PDF.")

        has_pdf = (
            (course and module and course in st.session_state.modules_by_course and
             module in st.session_state.modules_by_course[course])
            or (uploaded_pdf is not None)
        )

        if has_pdf:
            duration = st.number_input(
                "Focus Duration (minutes)",
                min_value=1,
                step=5,
                value=25,
                key="duration_input"
            )
            if st.button("Add Focus Session", key="add_session"):
                if course.strip() and module.strip():
                    st.session_state.sessions.append({
                        "course": course.strip(),
                        "module": module.strip(),
                        "duration": float(duration),
                    })
                    st.success("Focus session recorded!")
                else:
                    st.warning("Enter course and module name.")

        if st.session_state.sessions:
            st.subheader("Focus Sessions")
            df = pd.DataFrame(st.session_state.sessions)
            st.dataframe(df, use_container_width=True)

    with right:
        st.subheader("📚 Courses & Modules Dashboard")
        if st.session_state.modules_by_course:
            for c_name, modules in st.session_state.modules_by_course.items():
                with st.expander(f"📘 {c_name}", expanded=False):
                    if modules:
                        for m_name, meta in modules.items():
                            if st.button(f"📄 {m_name} → {meta['file_name']}", key=f"open_{c_name}_{m_name}"):
                                st.session_state.selected_course = c_name
                                st.session_state.selected_module = m_name
                                st.rerun()
                    else:
                        st.caption("No modules yet.")
        else:
            st.caption("No modules uploaded yet.")
        if st.session_state.selected_course and st.session_state.selected_module:
            c = st.session_state.selected_course
            m = st.session_state.selected_module
            if c in st.session_state.modules_by_course and m in st.session_state.modules_by_course[c]:
                meta = st.session_state.modules_by_course[c][m]
                st.markdown(f"**Preview: {m}**")
                st.markdown(
                    f"""
                    <iframe src="data:application/pdf;base64,{meta['base64']}"
                    width="400" height="500" type="application/pdf"></iframe>
                    """,
                    unsafe_allow_html=True
                )

# ---------------------------
# Personal Dashboard Page
# ---------------------------

elif st.session_state.page == "Personal Dashboard":

    st.header("📈 Personal Productivity Dashboard")

    col1, col2 = st.columns(2)

    with col1:
        st.write(f"Username: {st.session_state.username}")

    with col2:
        st.write(f"Email: {st.session_state.email}")

    total_sessions = len(st.session_state.sessions)
    if "modules_by_course" in st.session_state and st.session_state.modules_by_course:
        total_modules = sum(len(v) for v in st.session_state.modules_by_course.values())
    else:
        total_modules = len(st.session_state.modules)

    durations = [s["duration"] for s in st.session_state.sessions]

    total_duration = sum(durations)
    avg_focus = total_duration / total_sessions if total_sessions else 0

    m1, m2, m3 = st.columns(3)

    m1.metric("Total Focus Sessions", total_sessions)
    m2.metric("Average Focus Duration", f"{avg_focus:.1f} min")
    m3.metric("Total Uploaded Modules", total_modules)

    st.subheader("🧬 Distraction DNA Analysis")

    if total_sessions == 0:

        st.info("No productivity data available yet.")

    else:

        if avg_focus < 10:
            st.warning(f"🧬 Quick Distractor • Average: {avg_focus:.1f} min")
            st.write("Your focus sessions are short. Try 20-minute focus blocks.")

        elif avg_focus < 25:
            st.info(f"🧬 Balanced Learner • Average: {avg_focus:.1f} min")
            st.write("You maintain moderate focus. Increase session length gradually.")

        else:
            st.success(f"🧬 Deep Focus Achiever • Average: {avg_focus:.1f} min")
            st.write("Excellent concentration. Maintain your deep focus habits.")

    st.subheader("📊 Productivity Trend")

    if durations:

        chart_df = pd.DataFrame({
            "Focus Duration": durations
        })

        st.line_chart(chart_df)

    else:

        st.info("No productivity data available yet.")