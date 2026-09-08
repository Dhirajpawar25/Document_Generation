"""
Template Parser Module
Extracts structure and fixed phrases from the reference affidavit sample.
"""

import re
from typing import Any, Dict


def parse_reference_document(sample_text: str) -> Dict[str, Any]:
    """
    Parse the reference affidavit sample to extract structure.
    Returns a structured representation of the template.
    """
    template = {
        "sections": [],
        "fixed_phrases": {},
        "formatting_rules": {},
        "paragraph_structure": []
    }
    
    lines = [line.strip() for line in sample_text.strip().splitlines() if line.strip()]
    normalized_text = re.sub(r"\s+", " ", sample_text.strip())
    
    # Identify the 10 mandatory parts
    section_patterns = {
        "forum_heading": r"IN THE HIGH COURT OF JUDICATURE AT",
        "jurisdiction": r"JURISDICTION$",
        "case_number": r"(WRIT PETITION|PETITION) NO\.\s+\d+\s+OF\s+\d{4}",
        "cause_title_petitioner": r"\.\.\.Petitioner",
        "versus": r"^VERSUS$",
        "cause_title_respondent": r"\.\.\.Respondent No\.\d+",
        "affidavit_title": r"AFFIDAVIT IN REPLY ON BEHALF OF RESPONDENT NO\.",
        "deponent_clause": r"I, .+ do hereby (solemnly affirm|swear and affirm) and state as under:",
        "numbered_paragraph": r"^\d+\.\s+",
        "prayer_heading": r"^PRAYER$",
        "prayer_item": r"^\([a-z]\)\s+",
        "jurat": r"Solemnly affirmed at",
        "jurat_date": r"On this \d+(?:st|nd|rd|th) day of \w+ \d{4}",
        "before_me": r"Before Me",
        "deponent_signature": r"^DEPONENT$",
        "verification_heading": r"^VERIFICATION$",
        "verification_clause": r"I, .+ do hereby verify that the contents of paragraphs \d+ to \d+ and the Prayer above are true and correct",
        "verification_date": r"Verified at .+ on this \d+(?:st|nd|rd|th) day of \w+ \d{4}",
        "advocate_block": r"Advocates? for the Respondent"
    }
    
    section_order = [
        "forum_heading", "jurisdiction", "case_number", "cause_title",
        "affidavit_title", "deponent_clause", "numbered_paragraphs",
        "prayer", "jurat", "verification", "advocate_block",
    ]
    matches = {}
    for name, pattern in section_patterns.items():
        if name in {"deponent_clause", "verification_clause"}:
            matches[name] = bool(re.search(pattern, normalized_text, re.IGNORECASE))
        else:
            matches[name] = any(re.search(pattern, line, re.IGNORECASE) for line in lines)
    paragraph_numbers = [
        int(match.group(1))
        for line in lines
        if (match := re.match(r"^(\d+)\.\s+", line))
    ]
    prayer_letters = [
        match.group(1)
        for line in lines
        if (match := re.match(r"^\(([a-z])\)\s+", line, re.IGNORECASE))
    ]
    template["sections"] = section_order
    template["matches"] = matches
    template["paragraph_numbers"] = paragraph_numbers
    template["paragraph_count"] = len(paragraph_numbers)
    template["prayer_letters"] = prayer_letters
    template["fixed_phrases"] = {
        "deponent": "do hereby solemnly affirm and state as under",
        "verification": "true and correct to my knowledge and belief",
        "exhibit": "EXHIBIT-",
    }
    template["formatting_rules"] = {
        "headings": "bold uppercase centered",
        "body": "continuous numbered paragraphs",
        "prayer": "lettered items",
        "verification_range": "matches body paragraph count",
    }
    return template