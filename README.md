# LLM Comparative Experiment Pipeline

This repository contains a reproducible pipeline to compare Large Language Models (LLMs)
on narrative analysis tasks (chapter extraction, structured analysis using Greimas-inspired prompts,
validation and inter-judge comparison). The project uses OpenRouter-compatible providers for
unified API access and produces JSON outputs that can be inspected or used for downstream
validation.
Experiment outputs (JSON and HTML reports) are stored under `data/outputs/` and contain the
LLM analyses produced from the texts placed in `data/inputs/`.

## Key Concepts
- Extraction: split long texts into chapters/segments for analysis.
- Structured analysis: run guided prompts (Greimas-style) to get labelled, JSON-structured
	analyses from LLMs.
- Validation: compare multiple model outputs and run human/judge validation workflows.

## Repository Structure
- `src/` — main code and pipeline scripts.
- `src/greimas_pipeline/` — pipeline steps (01_extract_chapters.py, 02_run_structured_analysis.py,
	03_validate_analysis.py, 04_validate_holistic.py, 05_compare_judges.py).
- `validation_greimas_pipeline/` — helper runner(s) for JSON-structured experiments.
- `config/` — prompt templates and experiment configuration.
- `data/inputs/` — input text files to analyze.
- `data/outputs/` — folders with experiment JSON results and HTML reports.
- `data/ground_truth_chapters/` — example ground-truth chapter segmentation files.
- `VALIDATION_GUIDE.md` — notes and instructions for manual validation.

## Quickstart
1. Create and activate a virtual environment (recommended):

```powershell
python -m venv .venv
& .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Create a `.env` file at the project root and set your OpenRouter key (or other provider keys):

```
OPENROUTER_API_KEY=your_api_key_here
```

3. Place one or more text files into `data/inputs/`.

4. Run the main pipeline (example):

```powershell
python src/main.py
```

Or run individual pipeline steps for more control:

```powershell
python src/greimas_pipeline/01_extract_chapters.py
python src/greimas_pipeline/02_run_structured_analysis.py
```

5. Results and reports are saved under `data/outputs/` (each experiment run creates a timestamped
	 output folder with JSON files and optional HTML reports).

## Notes & Next Steps
- See `VALIDATION_GUIDE.md` for instructions on manual validation and judge comparison.
- Adjust prompt templates in `config/` to experiment with different instruction styles.
- Consider adding examples or a small sample run script for CI/integration tests.

