```markdown
# Validation Guide for Semiotic Analysis

This guide describes the steps required to run the semiotic analysis pipeline and validate
the results produced by an LLM against a reference text by A.J. Greimas.

## Prerequisites

Make sure you have a Python virtual environment configured and the dependencies installed.

1. **Activate the virtual environment**:
    ```powershell
    .\.venv\Scripts\Activate.ps1
    ```

## Validation Steps

The pipeline consists of three main phases.

### Phase 1: Sequence Extraction (Optional)

This step is necessary only if the input text is not already split into chapters or sequences.
The script `01_extract_chapters.py` splits a long text into separate text files, one per sequence.

1. **Run the script**:
    ```powershell
    python src/greimas_pipeline/01_extract_chapters.py "data/inputs/due_amici_maupassant.txt" "data/outputs/due_amici_chapters"
    ```
    - The first argument is the path to the input text file.
    - The second argument is the output directory where sequence files will be saved.

### Phase 2: Run Structured Analysis

This script takes a sequence (a text file) and uses an LLM to generate a structured semiotic
analysis in JSON format.

1. **Run the script**:
    ```powershell
    python src/greimas_pipeline/02_run_structured_analysis.py "data/outputs/due_amici_chapters/seq_01.txt" "openrouter/google/gemini-pro" "data/outputs/structured_analysis"
    ```
    - The first argument is the path to the sequence text file to analyze.
    - The second argument is the LLM model identifier (e.g. `openrouter/google/gemini-pro`, `anthropic/claude-3.5-sonnet`).
    - The third argument is the output directory where the JSON analysis file will be saved.

The output file will have a name similar to `structured_analysis_20260508_103000_google-gemini-pro.json`.

### Phase 3: Validation with LLM-Judge

This final script compares the LLM-generated analysis (the JSON from Phase 2) with the Greimas
reference ground truth. It uses another LLM as a “judge” to assess the analysis quality.

1. **Run the script**:
    ```powershell
    python src/greimas_pipeline/03_validate_analysis.py "data/outputs/structured_analysis/structured_analysis_20260508_103000_google-gemini-pro.json"
    ```
    - The sole argument is the path to the JSON file produced in Phase 2.

2. **Check the output**:
    The script will perform validation and save a new JSON file with the judge's evaluation
    in `data/outputs/validation_reports/`. The file name will include the date and model used,
    for example: `validation_20260508_103100_google-gemini-pro_structured_analysis.json`.

    This file contains scores and justifications for methodological adherence, conceptual
    correctness and coverage, together with an overall judgment.

```
