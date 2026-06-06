# LLM Comparative Experiment Pipeline

This project implements a reproducible pipeline for comparing Large Language Models (LLMs) on narrative analysis tasks, utilizing OpenRouter for unified API access.

## Structure
- `src/`: Source code.
- `data/inputs/`: Text files to analyze.
- `data/outputs/`: Experiment results (JSON).
- `config/`: Configuration files.

## Usage
1. Install dependencies: `pip install -r requirements.txt`
2. Create `.env` file with `OPENROUTER_API_KEY` (see `.env.example`).
3. Add text files to `data/inputs/`.
4. Run: `python src/main.py`

