"""Streamlit interface for the Legal Document Generation Agent."""

from pathlib import Path
import sys

import streamlit as st

# Streamlit runs this file from the app directory; add the repository root so
# the src package remains importable in local and Render deployments.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.legal_agent.pipeline import OUTPUTS, run_pipeline

st.set_page_config(page_title="Affidavit in Reply Agent", page_icon="A", layout="wide")
st.title("Affidavit in Reply Agent")
st.caption("Reference-guided generation, deterministic validation, and downloadable filing artifacts")

with st.sidebar:
    st.header("Inputs")
    use_demo = st.checkbox("Use supplied assignment files", value=True)
    reference_upload = st.file_uploader("Reference document text", type=["txt"])
    case_upload = st.file_uploader("Case information text", type=["txt"])
    st.info("The demo mode uses 02_sample.txt and 03_case.txt. Uploaded text files can be used to test another matter with the same schema.")

if use_demo or not (reference_upload and case_upload):
    reference_text = (ROOT / "data" / "text" / "02_sample.txt").read_text(encoding="utf-8")
    case_text = (ROOT / "data" / "text" / "03_case.txt").read_text(encoding="utf-8")
else:
    reference_text = reference_upload.getvalue().decode("utf-8")
    case_text = case_upload.getvalue().decode("utf-8")

if st.button("Generate and evaluate", type="primary"):
    try:
        result = run_pipeline(reference_text, case_text)
        report = result["report"]
        st.session_state["result"] = result
        st.success(f"Completed. Overall score: {report['overall_score']}/100")
    except Exception as error:
        st.error(f"Pipeline failed: {error}")

result = st.session_state.get("result")
if result:
    report = result["report"]
    left, right = st.columns([1, 2])
    with left:
        st.metric("Overall score", f"{report['overall_score']}/100")
        st.subheader("Dimension scores")
        for dimension, score in report["scores"].items():
            st.write(f"**{dimension}**: {score}/100")
        if report["issues"]:
            st.subheader("Issues detected")
            for issue in report["issues"]:
                st.warning(f"{issue['dimension']}: {issue['message']}")
        else:
            st.success("No deterministic validation issues detected.")
    with right:
        st.subheader("Generated affidavit")
        st.text_area("Preview", result["document"], height=620, label_visibility="collapsed")

    st.subheader("Downloads")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.download_button("Download DOCX", (OUTPUTS / "affidavit_in_reply.docx").read_bytes(), "affidavit_in_reply.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    with col2:
        st.download_button("Download evaluation report", (OUTPUTS / "evaluation_report.md").read_bytes(), "evaluation_report.md", "text/markdown")
    with col3:
        st.download_button("Download intermediate JSON", (OUTPUTS / "intermediate_data.json").read_bytes(), "intermediate_data.json", "application/json")
