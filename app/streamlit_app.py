"""Streamlit interface for the Legal Document Generation Agent."""

from pathlib import Path
from html import escape
import sys

import streamlit as st

# Streamlit runs this file from the app directory; add the repository root so
# the src package remains importable in local and Render deployments.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.legal_agent.document_loader import load_document
from src.legal_agent.pipeline import OUTPUTS, run_pipeline


def render_affidavit_preview(document: str) -> str:
    """Render generated affidavit text as a readable paper-style HTML preview."""
    rendered = []
    centered_headings = {
        "PRAYER",
        "VERIFICATION",
        "DEPONENT",
        "BEFORE ME",
    }
    for raw_line in document.splitlines():
        line = raw_line.strip()
        if not line:
            rendered.append('<div class="doc-spacer"></div>')
            continue

        safe_line = escape(line)
        upper_line = line.upper()
        if (
            upper_line in centered_headings
            or upper_line.startswith("IN THE ")
            or upper_line.endswith("JURISDICTION")
            or upper_line.startswith("AFFIDAVIT IN REPLY")
        ):
            rendered.append(f'<div class="doc-heading">{safe_line}</div>')
        elif line.startswith(("(", "1.", "2.", "3.", "4.", "5.", "6.", "7.")):
            rendered.append(f'<div class="doc-paragraph">{safe_line}</div>')
        else:
            rendered.append(f'<div class="doc-line">{safe_line}</div>')
    return '<div class="document-paper">' + "".join(rendered) + "</div>"

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
    [data-testid="stSidebar"] [data-testid="stFileUploaderFileName"] { color: var(--navy) !important; font-weight: 650; }
    [data-testid="stSidebar"] [data-testid="stFileUploaderFile"] { background: #ffffff; border: 1px solid var(--line); border-radius: 8px; }
    .uploaded-name { color: var(--navy); font-size: .78rem; font-weight: 650; margin: -.35rem 0 .7rem; }
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
    .check-card { background: var(--paper); border: 1px solid var(--line); border-radius: 10px; padding: .8rem 1rem; margin-bottom: .6rem; }
    .check-card.pass { border-left: 4px solid #0f766e; }
    .check-card.fail { border-left: 4px solid #dc2626; }
    .check-name { color: var(--navy); font-weight: 750; font-size: .9rem; }
    .check-status { float: right; font-size: .72rem; font-weight: 750; }
    .check-status.pass { color: #0f766e; }
    .check-status.fail { color: #dc2626; }
    .check-purpose { color: var(--slate); font-size: .78rem; margin: .3rem 0; }
    .check-evidence { color: #344256; font-size: .8rem; }
    .document-paper { background: #fff; border: 1px solid #d7dde5; border-radius: 4px; box-shadow: 0 8px 24px rgba(23,36,58,.08); color: #202938; font-family: Georgia, "Times New Roman", serif; line-height: 1.55; max-height: 700px; overflow-y: auto; padding: 2.4rem 3rem; }
    .doc-heading { font-family: Arial, sans-serif; font-size: .9rem; font-weight: 750; letter-spacing: .02em; margin: .25rem 0; text-align: center; }
    .doc-line { margin: .3rem 0; }
    .doc-paragraph { margin: .65rem 0; text-align: justify; }
    .doc-spacer { height: .65rem; }
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
    reference_upload = st.file_uploader(
        "Reference document",
        type=["txt", "pdf", "docx"],
        help="Accepted formats: TXT, PDF, and DOCX.",
    )
    if reference_upload:
        st.markdown(f'<div class="uploaded-name">Selected: {reference_upload.name}</div>', unsafe_allow_html=True)
    case_upload = st.file_uploader(
        "Case information",
        type=["txt", "pdf", "docx"],
        help="Accepted formats: TXT, PDF, and DOCX.",
    )
    if case_upload:
        st.markdown(f'<div class="uploaded-name">Selected: {case_upload.name}</div>', unsafe_allow_html=True)
    st.caption("Upload both documents. PDFs must contain selectable text; scanned PDFs need OCR.")
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
    if use_demo:
        reference_text = (ROOT / "data" / "text" / "02_sample.txt").read_text(encoding="utf-8")
        case_text = (ROOT / "data" / "text" / "03_case.txt").read_text(encoding="utf-8")
        source_label = "Supplied assignment documents"
        upload_ready = True
    else:
        reference_text = ""
        case_text = ""
        source_label = "Upload both source documents to continue"
        upload_ready = False
else:
    try:
        reference_text = load_document(reference_upload)
        case_text = load_document(case_upload)
        source_label = f"Uploaded documents · {reference_upload.name} + {case_upload.name}"
        upload_ready = True
    except ValueError as error:
        reference_text = ""
        case_text = ""
        source_label = str(error)
        upload_ready = False

source_col, action_col = st.columns([2.5, 1], vertical_alignment="bottom")
with source_col:
    st.markdown(f'<div class="panel"><div class="panel-title">Ready to process</div><span style="color:#56657a">{source_label} · Reference structure and case facts will be checked before generation.</span></div>', unsafe_allow_html=True)
with action_col:
    generate = st.button("Generate draft", type="primary", use_container_width=True, disabled=not upload_ready)

if generate:
    try:
        result = run_pipeline(reference_text, case_text)
        report = result["report"]
        st.session_state["result"] = result
        st.session_state["run_message"] = f"Draft generated and validated at {report['overall_score']}/100."
        st.session_state["run_failed"] = False
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
        passed_count = sum(1 for check in report["checks"] if check["passed"])
        st.metric("Checks passed", f"{passed_count}/{len(report['checks'])}")
    with summary_right:
        st.metric("Body paragraphs", str(report.get("reference_paragraph_count", 0)))

    left, right = st.columns([1, 2.1], gap="large")
    with left:
        st.markdown('<div class="section-label">Validation evidence</div>', unsafe_allow_html=True)
        st.caption("Each check compares the generated affidavit with the supplied case data and reference contract.")
        check_purposes = {
            "Entity Accuracy": "Confirms parties, deponent, designation, organisation, date, and exhibit appear in the output.",
            "Completeness": "Confirms the affidavit includes prayer, jurat, verification, and signature sections.",
            "Structure": "Confirms body paragraphs are continuous and match the expected sequence.",
            "Consistency": "Confirms the same answering respondent is used throughout the document.",
            "Template Fidelity": "Confirms lettered prayer items and the required exhibit convention are present.",
            "Reference Contract": "Confirms the uploaded reference contains the required affidavit sections.",
            "Input Coverage": "Confirms all six numbered reply points are present and contain facts.",
            "Hallucination Check": "Checks for unsupported statutory or case-law citation patterns.",
        }
        for check in report["checks"]:
            status_class = "pass" if check["passed"] else "fail"
            status_label = "PASS" if check["passed"] else "REVIEW"
            purpose = check_purposes.get(check["dimension"], "Deterministic validation of generated content.")
            st.markdown(
                f'<div class="check-card {status_class}">'
                f'<span class="check-status {status_class}">{status_label} · {report["scores"][check["dimension"]]}/100</span>'
                f'<div class="check-name">{check["dimension"]}</div>'
                f'<div class="check-purpose">{purpose}</div>'
                f'<div class="check-evidence"><strong>Result:</strong> {check["evidence"]}</div>'
                '</div>',
                unsafe_allow_html=True,
            )
        if report["issues"]:
            st.markdown('<div class="section-label">Review required</div>', unsafe_allow_html=True)
            for issue in report["issues"]:
                st.warning(f"{issue['dimension']}: {issue['message']}")
        else:
            st.success("All deterministic checks passed.")
    with right:
        st.markdown('<div class="section-label">Generated affidavit preview</div>', unsafe_allow_html=True)
        st.caption("Formatted review view. Download the DOCX draft for the final editable document.")
        st.markdown(render_affidavit_preview(result["document"]), unsafe_allow_html=True)

    st.markdown('<div class="section-label">Export artifacts</div>', unsafe_allow_html=True)
    st.caption("Download the draft and its supporting validation evidence for advocate review.")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.download_button("DOCX draft", (OUTPUTS / "affidavit_in_reply.docx").read_bytes(), "affidavit_in_reply.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)
    with col2:
        st.download_button("Validation report", (OUTPUTS / "evaluation_report.md").read_bytes(), "evaluation_report.md", "text/markdown", use_container_width=True)
    with col3:
        st.download_button("Intermediate JSON", (OUTPUTS / "intermediate_data.json").read_bytes(), "intermediate_data.json", "application/json", use_container_width=True)
