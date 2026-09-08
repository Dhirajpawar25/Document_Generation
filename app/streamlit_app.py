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

st.markdown(
    """
    <style>
    :root {
        --navy: #17243a;
        --slate: #56657a;
        --line: #dfe5ec;
        --paper: #ffffff;
        --canvas: #f5f7fa;
        --blue: #2563eb;
        --green: #0f766e;
    }
    .stApp { background: var(--canvas); }
    [data-testid="stHeader"] { background: rgba(245,247,250,.92); }
    [data-testid="stSidebar"] { background: #eef2f6; border-right: 1px solid var(--line); }
    [data-testid="stSidebar"] > div:first-child { padding-top: 2rem; }
    .brand { color: var(--navy); font-size: 1.7rem; font-weight: 750; letter-spacing: -.03em; }
    .eyebrow { color: var(--blue); font-size: .72rem; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; }
    .hero { padding: 1.4rem 0 1.8rem; }
    .hero h1 { color: var(--navy); font-size: 2.25rem; letter-spacing: -.045em; margin: .3rem 0 .5rem; }
    .hero p { color: var(--slate); font-size: 1rem; margin: 0; max-width: 720px; }
    .panel { background: var(--paper); border: 1px solid var(--line); border-radius: 12px; padding: 1.1rem 1.25rem; }
    .panel-title { color: var(--navy); font-size: 1rem; font-weight: 750; margin-bottom: .8rem; }
    .step { display: flex; gap: .7rem; align-items: flex-start; margin: .85rem 0; }
    .step-no { background: #dbeafe; color: #1d4ed8; border-radius: 50%; min-width: 1.5rem; height: 1.5rem; text-align: center; line-height: 1.5rem; font-weight: 750; font-size: .8rem; }
    .step strong { color: var(--navy); display: block; font-size: .9rem; }
    .step span { color: var(--slate); font-size: .78rem; }
    .score-card { background: #effcf9; border: 1px solid #b8e5da; border-radius: 12px; padding: 1rem; text-align: center; }
    .score-number { color: var(--green); font-size: 2.2rem; font-weight: 800; line-height: 1; }
    .score-label { color: #49675f; font-size: .75rem; margin-top: .4rem; }
    .section-label { color: var(--navy); font-size: 1.05rem; font-weight: 750; margin: 1.4rem 0 .7rem; }
    .stButton > button[kind="primary"] { border-radius: 8px; font-weight: 700; min-height: 2.7rem; }
    .stDownloadButton > button { border: 1px solid var(--line); border-radius: 8px; font-weight: 650; }
    div[data-testid="stMetric"] { background: var(--paper); border: 1px solid var(--line); border-radius: 10px; padding: .75rem 1rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown('<div class="brand">Affidavit<span style="color:#2563eb">.</span></div>', unsafe_allow_html=True)
    st.caption("Document preparation workspace")
    st.divider()
    st.markdown('<div class="eyebrow">01 / Source documents</div>', unsafe_allow_html=True)
    use_demo = st.checkbox("Use supplied assignment files", value=True)
    reference_upload = st.file_uploader("Reference document text", type=["txt"])
    case_upload = st.file_uploader("Case information text", type=["txt"])
    st.caption("Use the supplied demo files or upload both text files using the labeled case schema.")
    st.divider()
    st.markdown('<div class="eyebrow">02 / Workflow</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="step"><div class="step-no">1</div><div><strong>Read sources</strong><span>Parse reference and case facts</span></div></div>'
        '<div class="step"><div class="step-no">2</div><div><strong>Generate draft</strong><span>Map facts into affidavit structure</span></div></div>'
        '<div class="step"><div class="step-no">3</div><div><strong>Validate output</strong><span>Check accuracy and completeness</span></div></div>',
        unsafe_allow_html=True,
    )
    st.divider()
    st.caption("Deterministic workflow · No external API required")

st.markdown(
    '<div class="hero"><div class="eyebrow">Legal document workspace</div>'
    '<h1>Prepare an Affidavit in Reply</h1>'
    '<p>Generate a reference-guided draft, review validation evidence, and download filing-ready artifacts from one controlled workflow.</p></div>',
    unsafe_allow_html=True,
)

if use_demo or not (reference_upload and case_upload):
    reference_text = (ROOT / "data" / "text" / "02_sample.txt").read_text(encoding="utf-8")
    case_text = (ROOT / "data" / "text" / "03_case.txt").read_text(encoding="utf-8")
    source_label = "Supplied assignment documents"
else:
    reference_text = reference_upload.getvalue().decode("utf-8")
    case_text = case_upload.getvalue().decode("utf-8")
    source_label = "Uploaded documents"

source_col, action_col = st.columns([2.5, 1], vertical_alignment="bottom")
with source_col:
    st.markdown(f'<div class="panel"><div class="panel-title">Ready to process</div><span style="color:#56657a">{source_label} · Reference structure and case facts will be checked before generation.</span></div>', unsafe_allow_html=True)
with action_col:
    generate = st.button("Generate draft", type="primary", use_container_width=True)

if generate:
    try:
        result = run_pipeline(reference_text, case_text)
        report = result["report"]
        st.session_state["result"] = result
        st.session_state["run_message"] = f"Draft generated and validated at {report['overall_score']}/100."
    except Exception as error:
        st.session_state["run_message"] = f"Pipeline failed: {error}"
        st.session_state["run_failed"] = True

result = st.session_state.get("result")
if st.session_state.get("run_message"):
    if st.session_state.get("run_failed"):
        st.error(st.session_state["run_message"])
    else:
        st.success(st.session_state["run_message"])

if result:
    report = result["report"]
    st.markdown('<div class="section-label">Validation summary</div>', unsafe_allow_html=True)
    summary_left, summary_mid, summary_right = st.columns([1, 1, 1])
    with summary_left:
        st.markdown(f'<div class="score-card"><div class="score-number">{report["overall_score"]}<span style="font-size:1rem">/100</span></div><div class="score-label">Overall validation score</div></div>', unsafe_allow_html=True)
    with summary_mid:
        st.metric("Checks passed", f"{sum(report['scores'].values()) // 100}/{len(report['scores'])}")
    with summary_right:
        st.metric("Body paragraphs", str(report.get("reference_paragraph_count", 0)))

    left, right = st.columns([1, 2.1], gap="large")
    with left:
        st.markdown('<div class="section-label">Quality checks</div>', unsafe_allow_html=True)
        for dimension, score in report["scores"].items():
            st.progress(score / 100, text=f"{dimension} · {score}/100")
        if report["issues"]:
            st.markdown('<div class="section-label">Review required</div>', unsafe_allow_html=True)
            for issue in report["issues"]:
                st.warning(f"{issue['dimension']}: {issue['message']}")
        else:
            st.success("All deterministic checks passed.")
    with right:
        st.markdown('<div class="section-label">Generated affidavit</div>', unsafe_allow_html=True)
        st.text_area("Generated affidavit preview", result["document"], height=650, label_visibility="collapsed")

    st.markdown('<div class="section-label">Export artifacts</div>', unsafe_allow_html=True)
    st.caption("Download the draft and its supporting validation evidence for advocate review.")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.download_button("DOCX draft", (OUTPUTS / "affidavit_in_reply.docx").read_bytes(), "affidavit_in_reply.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)
    with col2:
        st.download_button("Validation report", (OUTPUTS / "evaluation_report.md").read_bytes(), "evaluation_report.md", "text/markdown", use_container_width=True)
    with col3:
        st.download_button("Intermediate JSON", (OUTPUTS / "intermediate_data.json").read_bytes(), "intermediate_data.json", "application/json", use_container_width=True)
