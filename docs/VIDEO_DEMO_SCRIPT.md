# Video Demo Script

## Suggested title

**Legal Document Generation Agent: Reference-Guided Affidavit in Reply**

## Target duration

Three to five minutes.

## Script and screen directions

### 0:00-0:20 - Introduction

**On screen:** Repository README or the deployed application landing page.

**Narration:**  
“This is the Legal Document Generation Agent. It generates an Affidavit in Reply from a reference affidavit and structured case information. The workflow is deterministic, reproducible, and includes validation so the generated document can be reviewed before download.”

### 0:20-0:50 - Explain the inputs

**On screen:** Streamlit sidebar with “Use supplied assignment files” enabled.

**Narration:**  
“The demo uses two inputs: a reference document that defines the structure and formatting conventions, and case information containing the court, parties, deponent, dates, advocate, and reply points. The application also supports uploading text files that follow the same labels.”

### 0:50-1:25 - Run generation

**Action:** Click **Generate and evaluate**.

**Narration:**  
“I’ll now run the supplied demo. The pipeline parses the reference, extracts the case entities, maps the six reply points into the reference document moves, renders the affidavit text and DOCX, and evaluates the result.”

### 1:25-2:10 - Show the generated affidavit

**On screen:** Generated affidavit preview.

**Narration:**  
“The preview preserves the expected affidavit structure: court heading, case number, cause title, deponent clause, continuous numbered paragraphs, a lettered prayer, jurat, verification, and advocate block. The answering party remains Respondent No. 2 throughout.”

### 2:10-2:50 - Explain validation

**On screen:** Overall score, dimension scores, and issue list.

**Narration:**  
“The evaluation uses eight deterministic dimensions: entity accuracy, completeness, structure, answering-respondent consistency, template fidelity, reference-contract completeness, reply-point coverage, and hallucination risk. Each check includes evidence, and any failed check appears as an issue instead of being hidden.”

### 2:50-3:20 - Show downloads

**Action:** Point to the DOCX, evaluation report, and intermediate JSON download buttons.

**Narration:**  
“The user can download three artifacts: the formatted DOCX for review, the Markdown evaluation report, and the intermediate JSON representation used by the pipeline. This makes the workflow auditable and easy to integrate into a review process.”

### 3:20-3:50 - Demonstrate upload mode

**Action:** Disable demo mode, upload a reference text file and a case text file, then run again.

**Narration:**  
“For another matter, I can turn off demo mode and upload text files using the same labeled schema. The application does not perform independent legal research or invent facts; it works from the supplied inputs and keeps advocate review in the loop.”

### 3:50-4:10 - Close with limitations

**On screen:** README limitations or deployed URL.

**Narration:**  
“This is a proof of concept for the supplied Affidavit in Reply schema. It is not legal advice, does not replace advocate review, and does not yet support arbitrary document types or paragraph-wise petition matching. The deployed demo is available at the project’s Render URL.”

## Recording checklist

- Show the application URL or local Streamlit URL.
- Keep the generated score and all six dimensions visible.
- Open the DOCX download only if the recording needs to demonstrate the final file.
- Do not show secrets, local environment files, or private case data.
- End with the repository README link and the deployed application link.
