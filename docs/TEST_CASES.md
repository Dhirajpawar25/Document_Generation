# Application Test Cases

These cases are designed for manual execution through Streamlit and for direct pipeline verification. The supplied `data/text/02_sample.txt` and `data/text/03_case.txt` files are the baseline happy path.

| ID | Scenario | Setup | Expected result |
| --- | --- | --- | --- |
| TC-01 | Generate supplied demo | Enable demo mode and click **Generate and evaluate** | Generation succeeds, preview is populated, outputs are written, and the score is displayed |
| TC-02 | Verify entity accuracy | Run TC-01 | Output contains Sunrise Housing Private Limited, Mumbai Metropolitan Region Development Authority, Arvind Rajan, Deputy Metropolitan Commissioner, 15 July 2026, and EXHIBIT-‘A’ |
| TC-03 | Verify document structure | Run TC-01 and inspect preview | Body paragraphs are numbered 1 through 7, followed by PRAYER, `(a)` through `(c)`, jurat, verification, and advocate block |
| TC-04 | Verify respondent consistency | Run TC-01 and search the preview for respondent references | Every answering-party reference is Respondent No. 2; no Respondent No. 3 reference is present |
| TC-05 | Verify downloads | Run TC-01 and download all three artifacts | DOCX opens as a Word document; JSON is valid; Markdown report contains scores, checks, and issues |
| TC-06 | Upload equivalent inputs | Disable demo mode and upload copies of the sample reference and case text | Output is equivalent to the demo result for the same inputs |
| TC-07 | Missing reference upload | Disable demo mode and upload only a case file | The UI does not silently claim a custom run; it falls back to demo mode because both uploads are required |
| TC-08 | Missing case upload | Disable demo mode and upload only a reference file | The UI does not silently claim a custom run; it falls back to demo mode because both uploads are required |
| TC-09 | Malformed case labels | Upload a case file with a missing `Petitioner` or `Name` label | The run fails visibly or produces a failed validation; no invented value appears in the document |
| TC-10 | Malformed reference structure | Upload a reference without PRAYER or VERIFICATION | The run is visible to the user and the evaluation reports template/completeness problems |
| TC-11 | Wrong answering respondent | Change `Acting for` or respondent data inconsistently | Consistency or entity checks fail rather than silently normalizing the conflict |
| TC-12 | Missing exhibit convention | Remove the exhibit marker from the reference or case input | Template fidelity fails and the issue identifies the missing exhibit convention |
| TC-13 | Hallucination guard | Add a statutory provision not present in the supplied facts | Hallucination check fails or flags the suspicious statutory language |
| TC-14 | Date and verification output | Run TC-01 | The jurat and verification use Mumbai and 5th day of September 2026 and the verification range matches seven body paragraphs |
| TC-15 | Render deployment smoke test | Open the Render URL, run TC-01, and download DOCX | Service loads, generation completes, and downloads are available after a possible cold start |

## Post-run checks

1. Confirm `outputs/affidavit_in_reply.docx`, `outputs/intermediate_data.json`, and `outputs/evaluation_report.md` have updated timestamps.
2. Confirm the report contains eight dimensions and an overall score from 50 to 100.
3. Confirm no API key or private source file is displayed in the recording or committed to the repository.
