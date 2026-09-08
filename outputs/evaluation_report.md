# Evaluation Report

**Overall Score: 81/100**

- **Entity Accuracy:** 50/100
- **Completeness:** 100/100
- **Structure:** 100/100
- **Consistency:** 100/100
- **Template Fidelity:** 100/100
- **Reference Contract:** 50/100
- **Input Coverage:** 50/100
- **Hallucination Check:** 100/100

## Issues Detected
- Entity Accuracy: Missing required case fields: deponent.
- Reference Contract: Missing reference elements: cause_title_respondent.
- Input Coverage: Reply point numbers: [1, 2, 3, 5, 6, 7]; each point has facts: False.

Scoring: each deterministic dimension scores 100 when its checks pass and 50 when it fails; the overall score is the mean of six dimensions.