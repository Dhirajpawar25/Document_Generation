# Architecture Diagram

This application is a local-first Streamlit workflow for generating an Affidavit in Reply from a reference document and structured case information. It produces a DOCX, intermediate JSON, and deterministic evaluation report without requiring an external AI API.

## Application Architecture

<!-- mermaid-checked: no \n, no em-dash/en-dash, no {} in labels, subgraphs are id["label"], arrows are -->|"label"|, all subgraphs closed by end, ids unique -->
~~~mermaid
flowchart TD
    subgraph ClientLayer["Client Layer"]
        Browser["Web Browser"]
        Streamlit["Streamlit UI"]
    end
    subgraph AppLayer["Application Layer"]
        Ingest["Text Input Ingestion"]
        Parser["Reference Template Parser"]
        Extractor["Case Entity Extractor"]
        Mapper["Content Mapping Engine"]
        Generator["Document Generator"]
        Validator["Deterministic Validation"]
    end
    subgraph DataLayer["Data Layer"]
        SourceFiles[("Reference and Case Text")]
        Outputs[("Generated Outputs")]
    end
    subgraph RuntimeLayer["Runtime and Deployment"]
        Python["Python 3.11"]
        Render["Render Web Service"]
    end

    Browser -->|"opens"| Streamlit
    Streamlit -->|"uploads or selects demo files"| Ingest
    Ingest -->|"reads"| SourceFiles
    Ingest -->|"reference text"| Parser
    Ingest -->|"case text"| Extractor
    Parser -->|"template contract"| Mapper
    Extractor -->|"structured facts"| Mapper
    Mapper -->|"mapped reply content"| Generator
    Generator -->|"affidavit text and DOCX"| Outputs
    Generator -->|"generated text"| Validator
    Parser -->|"structure expectations"| Validator
    Extractor -->|"entity expectations"| Validator
    Validator -->|"scores and issues"| Outputs
    Python -->|"runs"| Streamlit
    Render -->|"hosts"| Streamlit
~~~

### Technology Stack Summary

| Layer | Technology | Version | Purpose |
| --- | --- | --- | --- |
| UI | Streamlit | 1.39.0 | Demo mode, text uploads, preview, scores, and downloads |
| Runtime | Python | 3.11.9 on Render | Executes the application and pipeline |
| Document output | python-docx | 1.1.2 | Writes the generated affidavit as DOCX |
| Source extraction utility | pdfplumber | 0.11.4 | Optional one-time PDF-to-text fixture extraction |
| Application logic | Python modules | Repository source | Parses, extracts, maps, renders, and evaluates |
| Hosting | Render web service | Free plan | Runs Streamlit with an assigned port |

### Data Storage & External Services

The application uses checked-in text fixtures under `data/text/` as its runtime source and writes generated artifacts under `outputs/`. It does not use a database, cache, message broker, or external API. Render provides hosting only; the demo is deliberately reproducible and does not require an API key.

### Key Architectural Decisions

- A structured intermediate entity dictionary separates extraction from document rendering.
- Deterministic templates and validation keep output repeatable and make issues explainable.
- PDF parsing is kept out of the request path; checked-in text fixtures make deployment reliable.

## Component Relationships

<!-- mermaid-checked: no \n, no em-dash/en-dash, no {} in labels, subgraphs are id["label"], arrows are -->|"label"|, all subgraphs closed by end, ids unique -->
~~~mermaid
flowchart LR
    subgraph cPresentation["Presentation"]
        cApp["streamlit_app.py"]
        cInputs["Demo or Upload Inputs"]
        cDownloads["Preview and Downloads"]
    end
    subgraph cBusiness["Business Logic"]
        cPipeline["pipeline.py"]
        cParser["parse_reference_document"]
        cExtractor["extract_case_entities"]
        cMapper["map_content"]
        cRender["render_text and write_docx"]
        cEvaluate["evaluate"]
    end
    subgraph cData["Data Access"]
        cFixtures["data/text Fixtures"]
        cArtifacts["outputs Artifacts"]
    end
    subgraph cInfra["Infrastructure"]
        cPdf["extract_pdfs.py"]
        cRenderHost["render.yaml"]
    end

    cApp -->|"reads"| cInputs
    cInputs -->|"passes text"| cPipeline
    cPipeline -->|"calls"| cParser
    cPipeline -->|"calls"| cExtractor
    cParser -->|"template data"| cMapper
    cExtractor -->|"entity data"| cMapper
    cMapper -->|"mapped document data"| cRender
    cRender -->|"text and DOCX"| cArtifacts
    cPipeline -->|"runs checks"| cEvaluate
    cParser -->|"reference expectations"| cEvaluate
    cExtractor -->|"entity expectations"| cEvaluate
    cFixtures -->|"loaded by UI or pipeline"| cInputs
    cArtifacts -->|"downloaded by UI"| cDownloads
    cPdf -->|"creates fixtures"| cFixtures
    cRenderHost -->|"configures hosting"| cApp
~~~

### Component Inventory

| Component | Layer | Type | Responsibility |
| --- | --- | --- | --- |
| `app/streamlit_app.py` | Presentation | UI entry point | Presents inputs, runs the pipeline, displays scores, and exposes downloads |
| `run_pipeline` in `pipeline.py` | Business Logic | Orchestrator | Coordinates parsing, extraction, mapping, rendering, evaluation, and file writes |
| `parse_reference_document` | Business Logic | Parser | Detects section order, paragraph numbering, prayer letters, and fixed phrases |
| `extract_case_entities` | Business Logic | Extractor | Converts labeled case text into a structured entity dictionary |
| `map_content` | Business Logic | Mapper | Converts reply points into fixed legal-document moves |
| `render_text` | Business Logic | Renderer | Builds the affidavit text with numbering, prayer, jurat, and verification |
| `write_docx` | Business Logic | Renderer | Creates the formatted Word artifact |
| `evaluate` | Business Logic | Validator | Scores entity accuracy, completeness, structure, consistency, fidelity, and hallucination risk |
| `data/text/` | Data Access | Fixtures | Stores reproducible reference and case text |
| `outputs/` | Data Access | Artifacts | Stores DOCX, JSON, text, and Markdown evaluation outputs |
| `scripts/extract_pdfs.py` | Infrastructure | Utility | Extracts supplied PDFs into text fixtures |
| `render.yaml` | Infrastructure | Deployment config | Defines Render build, start command, and Python version |
