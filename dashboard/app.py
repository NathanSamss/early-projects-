"""
dashboard/app.py
Streamlit dashboard. Shows applications by status and track, and lets you
see which jobs need manual finishing (CAPTCHA / Workday).
Run: streamlit run dashboard/app.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
from database.models.base import init_db
from database.repositories.application_repo import ApplicationRepository
from database.repositories.job_repo import JobRepository
from services.analytics.analytics_service import AnalyticsService

init_db()

st.set_page_config(page_title="Auto-Apply Dashboard", page_icon="🛡️", layout="wide")
st.title("Resume Auto-Apply Dashboard")

analytics = AnalyticsService()
app_repo = ApplicationRepository()
job_repo = JobRepository()

summary = analytics.summary()

col1, col2, col3 = st.columns(3)
col1.metric("Total Applications", summary["total_applications"])
col2.metric("Tracks Active", len([k for k in summary["by_track"] if k]))
col3.metric("Applied", summary["by_status"].get("applied", 0))

st.subheader("By Track")
st.bar_chart(summary["by_track"])

st.subheader("By Status")
st.bar_chart(summary["by_status"])

st.subheader("Needs Manual Finish")
manual = app_repo.by_status("pending_manual")
if manual:
    for a in manual:
        job = job_repo.get(a.job_id)
        if job:
            st.write(f"**{job.title}** @ {job.company} — {a.platform} — {a.notes}")
            st.write(job.url)
else:
    st.write("Nothing pending manual finish.")
