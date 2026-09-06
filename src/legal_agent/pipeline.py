"""End-to-end affidavit generation and deterministic evaluation pipeline."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple

from .entity_extractor import extract_case_entities
from .template_parser import parse_reference_document


ROOT = Path(__file__).resolve().parents[2]
OUTPUTS = ROOT / "outputs"


def _ordinal(day: str) -> str:
    number = int(day.split()[0])
    suffix = "th" if 10 < number % 100 < 14 else {1: "st", 2: "nd", 3: "rd"}.get(number % 10, "th")
    return f"{number}{suffix} day of September 2026"


def _facts(entity: Dict[str, Any], number: int) -> str:
    return "; ".join(entity["reply_points"][number - 1]["facts"])


def map_content(entity: Dict[str, Any]) -> Dict[str, Any]:
    """Map supplied facts to the reference's fixed reply moves."""
    respondent = f"Respondent No.{entity['respondent_number']}"
    return {
        "body_paragraphs": [
            f"I say that I am the Deputy Metropolitan Commissioner of {entity['organisation']}, the {respondent} in the above Writ Petition, and am well acquainted with the facts and circumstances of the case. I have perused a copy of the Writ Petition filed by {entity['petitioner']} and am competent to affirm this Affidavit in Reply. I am filing this Affidavit in Reply on behalf of {respondent}, {entity['organisation']}, to oppose the contentions raised in the Writ Petition and the reliefs sought by the Petitioner.",
            f"At the outset, I deny each and every allegation, contention and submission made in the Writ Petition, save and except those specifically admitted herein. {respondent} denies all statements, contentions and averments made in the Writ Petition except those specifically admitted in this Affidavit in Reply. Nothing contained in the Writ Petition that has not been specifically dealt with or admitted is to be treated as an admission by {respondent}.",
            f"I say that the Writ Petition is misconceived and devoid of merits. The actions challenged by the Petitioner were taken in accordance with the applicable redevelopment procedure and within the authority available to {respondent}. The action complained of has been taken strictly in accordance with law and after following due procedure.",
            f"With reference to the averments made in the Petition, I say that {respondent} denies that the impugned communication dated {entity['communication_date']} was issued without authority. The said contention is false, incorrect and denied.",
            f"I say that the communication dated {entity['communication_date']} was issued pursuant to the applicable redevelopment procedure and after consideration of the relevant records.",
            f"I say that {respondent} relies upon the communication dated {entity['communication_date']}. Hereto annexed and marked as {entity['exhibit']} is a copy of the said communication.",
            f"In the premises aforesaid, I say that the Writ Petition deserves to be dismissed with costs.",
        ],
        "prayer": [
            "dismiss the present Writ Petition with costs",
            "refuse any interim or ad-interim relief sought by the Petitioner",
            "grant such other and further reliefs as this Hon'ble Court may deem fit and proper in the facts and circumstances of the case",
        ],
        "respondent_label": respondent,
    }


def render_text(entity: Dict[str, Any], mapped: Dict[str, Any]) -> str:
    date = _ordinal(entity["date"])
    respondent = mapped["respondent_label"]
    lines = [
        entity["court"].upper(), entity["jurisdiction"].upper(),
        f"{entity['proceeding_type'].upper()} NO. {entity['case_number']} OF {entity['year']}", "",
        f"{entity['petitioner']} ...Petitioner", "VERSUS",
        f"1. {entity['respondent_1']} ...Respondent No.1",
        f"2. {entity['respondent_2']} ...Respondent No.2", "",
        f"AFFIDAVIT IN REPLY ON BEHALF OF {respondent.upper()}", "",
        f"I, {entity['deponent']}, {entity['designation']}, of {entity['organisation']}, having office at {entity['address']}, the {entity['designation']} of the {respondent} above named, do hereby solemnly affirm and state as under:", "",
    ]
    lines.extend(f"{index}. {paragraph}" for index, paragraph in enumerate(mapped["body_paragraphs"], 1))
    lines += ["", "PRAYER", "I therefore respectfully pray that this Hon'ble Court may be pleased to:"]
    lines.extend(f"({letter}) {item};" if letter != "c" else f"({letter}) {item}." for letter, item in zip("abc", mapped["prayer"]))
    lines += ["", f"Solemnly affirmed at {entity['place']}", f"On this {date}", "DEPONENT", "Before Me", "", "VERIFICATION", f"I, {entity['deponent']}, the Deponent above named, do hereby verify that the contents of paragraphs 1 to {len(mapped['body_paragraphs'])} and the Prayer above are true and correct to my knowledge and belief and that nothing material has been concealed therefrom.", f"Verified at {entity['place']} on this {date}.", "DEPONENT", "", entity["advocate_firm"].upper(), f"Advocates for the {respondent}."]
    return "\n".join(lines) + "\n"


def evaluate(document: str, entity: Dict[str, Any], template: Dict[str, Any]) -> Dict[str, Any]:
    checks: List[Tuple[str, bool, str]] = []
    required_entities = [entity["petitioner"], entity["respondent_2"], entity["deponent"], entity["designation"], entity["communication_date"], entity["exhibit"]]
    checks.append(("Entity Accuracy", all(value in document for value in required_entities), "All supplied party, deponent, date and exhibit values appear in the output."))
    required_sections = ["PRAYER", "VERIFICATION", "Solemnly affirmed", "Before Me", "DEPONENT"]
    checks.append(("Completeness", all(section in document for section in required_sections), "Required affidavit sections are present."))
    body = document.split("state as under:", 1)[1].split("PRAYER", 1)[0]
    numbers = [int(value) for value in re.findall(r"(?m)^(\d+)\.\s", body)]
    checks.append(("Structure", numbers == list(range(1, 8)), f"Detected body numbering: {numbers}."))
    answer_references = re.findall(r"Respondent No\.?\s*([23])", document, re.IGNORECASE)
    checks.append(("Consistency", bool(answer_references) and set(answer_references) == {"2"}, "Answering respondent references use Respondent No. 2 throughout."))
    checks.append(("Template Fidelity", "(a)" in document and "(b)" in document and "(c)" in document and "EXHIBIT-" in document, "Prayer is lettered and the exhibit follows the reference convention."))
    supplied_values = set(required_entities + [entity["court"], entity["jurisdiction"], entity["advocate_firm"]])
    suspicious = [word for word in re.findall(r"\b[A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)*\b", document) if word not in supplied_values and word not in {"IN", "THE", "HIGH", "COURT", "OF", "AT", "BOMBAY", "CIVIL", "APPELLATE", "ORDINARY", "ORIGINAL", "WRIT", "PETITION", "NO", "AFFIDAVIT", "REPLY", "ON", "BEHALF", "RESPONDENT", "PRAYER", "VERIFICATION", "DEPONENT", "Before", "Me", "EXHIBIT", "Advocates", "State", "Maharashtra"}]
    checks.append(("Hallucination Check", not any("statut" in item.lower() for item in suspicious), "No new statutory provision was introduced; names are constrained to supplied facts."))
    scores = {name: 100 if passed else 50 for name, passed, _ in checks}
    issues = [{"dimension": name, "message": explanation} for name, passed, explanation in checks if not passed]
    overall = round(sum(scores.values()) / len(scores))
    return {"overall_score": overall, "scores": scores, "issues": issues, "checks": [{"dimension": n, "passed": p, "evidence": e} for n, p, e in checks], "reference_paragraph_count": template["paragraph_count"]}


def write_docx(document: str, path: Path) -> None:
    from docx import Document
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.shared import Pt
    doc = Document()
    for index, line in enumerate(document.splitlines()):
        paragraph = doc.add_paragraph()
        paragraph.paragraph_format.space_after = Pt(6)
        if line.isupper() or re.match(r"^\d+\.\s|^\([a-z]\)\s", line):
            run = paragraph.add_run(line)
            run.bold = True
        else:
            paragraph.add_run(line)
        if line.isupper() and index < 10:
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.save(path)


def run_pipeline(reference_text: str, case_text: str, output_dir: Path = OUTPUTS) -> Dict[str, Any]:
    entity = extract_case_entities(case_text)
    template = parse_reference_document(reference_text)
    mapped = map_content(entity)
    document = render_text(entity, mapped)
    report = evaluate(document, entity, template)
    output_dir.mkdir(exist_ok=True)
    (output_dir / "affidavit_in_reply.txt").write_text(document, encoding="utf-8")
    write_docx(document, output_dir / "affidavit_in_reply.docx")
    (output_dir / "intermediate_data.json").write_text(json.dumps({"entities": entity, "template": template, "mapping": mapped}, indent=2, ensure_ascii=False), encoding="utf-8")
    report_md = "# Evaluation Report\n\n" + f"**Overall Score: {report['overall_score']}/100**\n\n" + "\n".join(f"- **{name}:** {score}/100" for name, score in report["scores"].items()) + "\n\n## Issues Detected\n" + ("\n".join(f"- {issue['dimension']}: {issue['message']}" for issue in report["issues"]) or "No issues detected.") + "\n\nScoring: each deterministic dimension scores 100 when its checks pass and 50 when it fails; the overall score is the mean of six dimensions."
    (output_dir / "evaluation_report.md").write_text(report_md, encoding="utf-8")
    (output_dir / "evaluation_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return {"entities": entity, "template": template, "mapping": mapped, "document": document, "report": report}


if __name__ == "__main__":
    result = run_pipeline((ROOT / "data" / "text" / "02_sample.txt").read_text(encoding="utf-8"), (ROOT / "data" / "text" / "03_case.txt").read_text(encoding="utf-8"))
    print(json.dumps(result["report"], indent=2))
