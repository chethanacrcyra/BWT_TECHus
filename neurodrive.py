import streamlit as st
import pandas as pd
from datetime import datetime

# ------------------------------------------------------------
# NeuroDrive DNA – AI Productivity Analyzer
# Single-file Streamlit app that tracks focus sessions,
# analyzes Distraction DNA, and visualizes productivity.
# ------------------------------------------------------------

# --------------- Session State Initialization ---------------
if "sessions" not in st.session_state:
    # Each session: {"course": str, "module": str, "duration": float, "timestamp": datetime}
    st.session_state.sessions = []

# -------------------------- Title ---------------------------
st.set_page_config(page_title="NeuroDrive DNA", layout="wide")
st.title("NeuroDrive DNA – AI Productivity Analyzer")
st.caption("Analyze focus behavior and generate a Distraction DNA profile.")

# ---------------------- Helper Functions --------------------
def compute_metrics(sessions: list[dict]) -> dict:
    """Compute total sessions, average duration, and longest duration."""
    if not sessions:
        return {"total": 0, "avg": 0.0, "max": 0.0}
    durations = [s["duration"] for s in sessions]
    total = len(durations)
    avg = float(pd.Series(durations).mean())
    longest = float(max(durations))
    return {"total": total, "avg": avg, "max": longest}


def classify_dna(avg_minutes: float) -> tuple[str, str, str]:
    """
    Classify Distraction DNA based on average focus duration.
    Returns: (label_with_emoji, color, suggestion)
    """
    if avg_minutes < 10:
        return ("🧬 Quick Distractor", "warning", "Your focus sessions are short. Try 20 minute focus blocks.")
    if 10 <= avg_minutes <= 25:
        return ("🧬 Balanced Learner", "info", "You maintain moderate focus. Increase session length gradually.")
    return ("🧬 Deep Focus Achiever", "success", "Excellent concentration. Maintain your deep focus habits.")


def sessions_dataframe(sessions: list[dict]) -> pd.DataFrame:
    """Convert session list to DataFrame, sorted by timestamp."""
    if not sessions:
        return pd.DataFrame(columns=["Timestamp", "Course", "Module", "Duration (min)"])
    df = pd.DataFrame(
        [{
            "Timestamp": s["timestamp"],
            "Course": s["course"],
            "Module": s["module"],
            "Duration (min)": s["duration"],
        } for s in sessions]
    ).sort_values("Timestamp")
    return df.reset_index(drop=True)


# -------------------------- Layout --------------------------
left, right = st.columns([2, 1], gap="large")

# ------------------------ Input Panel -----------------------
with left:
    st.subheader("Focus Session Input")
    with st.form("focus_form", clear_on_submit=True):
        course = st.text_input("Course name")
        module = st.text_input("Module name")
        duration = st.number_input("Focus duration (minutes)", min_value=1, max_value=500, value=25, step=1)
        submitted = st.form_submit_button("Add Focus Session")
        if submitted:
            # Validate minimal fields
            if len(course.strip()) == 0 or len(module.strip()) == 0:
                st.error("Please enter both course and module names.")
            else:
                st.session_state.sessions.append({
                    "course": course.strip(),
                    "module": module.strip(),
                    "duration": float(duration),
                    "timestamp": datetime.now(),
                })
                st.success("Session added.")

# ------------------------ Dashboard -------------------------
with left:
    st.subheader("Focus Session Dashboard")
    df = sessions_dataframe(st.session_state.sessions)
    if df.empty:
        st.info("No sessions yet. Add your first focus session to begin.")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)

        # Summary metrics
        metrics = compute_metrics(st.session_state.sessions)
        m1, m2, m3 = st.columns(3)
        m1.metric("Total sessions", metrics["total"])
        m2.metric("Average focus time (min)", f'{metrics["avg"]:.1f}')
        m3.metric("Longest session (min)", f'{metrics["max"]:.1f}')

        # Productivity visualization
        st.markdown("**Productivity Visualization**")
        chart_df = pd.DataFrame({
            "Duration (min)": df["Duration (min)"].values,
        })
        # Simple 3-session rolling average as trend (NaN filled with same value for short series)
        trend = pd.Series(chart_df["Duration (min)"]).rolling(window=3, min_periods=1).mean()
        chart_df["Trend"] = trend
        st.line_chart(chart_df, use_container_width=True)

# --------------------- DNA Analyzer Panel -------------------
with right:
    st.subheader("Distraction DNA Analyzer")
    analyze = st.button("Analyze Cognitive DNA")
    if analyze:
        metrics = compute_metrics(st.session_state.sessions)
        avg = metrics["avg"]
        label, color, suggestion = classify_dna(avg)

        # Colored result box
        if color == "success":
            st.success(f"{label}\n\nAverage focus duration: {avg:.1f} minutes")
        elif color == "info":
            st.info(f"{label}\n\nAverage focus duration: {avg:.1f} minutes")
        else:
            st.warning(f"{label}\n\nAverage focus duration: {avg:.1f} minutes")

        # Smart Productivity Notification
        st.markdown("### Smart Productivity Notification")
        st.write(suggestion)
    else:
        st.caption("Click Analyze Cognitive DNA to classify your focus pattern.")

# ---------------------- Footer / Tip ------------------------
st.divider()
st.caption("Data is stored in-memory for this session using Streamlit session_state.")