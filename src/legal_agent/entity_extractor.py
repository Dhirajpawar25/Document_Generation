import re
from typing import Any, Dict

"""Deterministic entity extraction for the supplied assignment documents."""

def extract_case_entities(case_text: str) -> Dict[str, Any]:
	"""Extract the known case schema without inventing legal facts."""
	lines = [line.strip() for line in case_text.splitlines() if line.strip()]

	def line_value(prefix: str) -> str:
		for line in lines:
			if line.lower().startswith(prefix.lower()):
				return line[len(prefix):].strip()
		return ""

	points = []
	point_pattern = re.compile(r"Point\s+(\d+)\s+[—-]\s+(.+)", re.IGNORECASE)
	for index, line in enumerate(lines):
		match = point_pattern.match(line)
		if match:
			bullets = []
			for following in lines[index + 1:]:
				if point_pattern.match(following) or following.startswith("4. Prayer"):
					break
				if following.startswith("●"):
					bullets.append(following.lstrip("● "))
			points.append({"number": int(match.group(1)), "title": match.group(2), "facts": bullets})

	communication_match = re.search(
		r"communication dated\s+(\d{1,2}\s+[A-Za-z]+\s+\d{4})",
		case_text,
		re.IGNORECASE,
	)
	exhibit_match = re.search(r"EXHIBIT[- ]['‘\"�]?([A-Z])", case_text, re.IGNORECASE)
	prayer_match = re.search(r"4\.\s+Prayer\s+(.+?)(?:\n5\.\s+Attestation|\Z)", case_text, re.IGNORECASE | re.DOTALL)

	return {
		"document_type": line_value("Document Type"),
		"court": line_value("Court"),
		"jurisdiction": line_value("Jurisdiction"),
		"proceeding_type": line_value("Proceeding Type"),
		"case_number": line_value("Case Number"),
		"year": line_value("Year"),
		"petitioner": line_value("Petitioner"),
		"respondent_1": line_value("Respondent No. 1"),
		"respondent_2": line_value("Respondent No. 2"),
		"respondent_number": "2",
		"deponent": line_value("Name"),
		"designation": line_value("Designation"),
		"organisation": line_value("Organisation"),
		"address": line_value("Address"),
		"verification_verb": line_value("Verification verb"),
		"place": line_value("Place"),
		"date": line_value("Date"),
		"advocate_firm": line_value("Advocate Firm"),
		"acting_for": line_value("Acting for"),
		"communication_date": communication_match.group(1) if communication_match else "",
		"exhibit": f"EXHIBIT-‘{exhibit_match.group(1).upper()}’" if exhibit_match else "",
		"prayer_text": prayer_match.group(1).strip() if prayer_match else "",
		"reply_points": points,
	}
