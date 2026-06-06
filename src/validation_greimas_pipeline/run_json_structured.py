"""
Run del prompt JSON strutturato (PROMPT_GREIMAS_JSON_STRUTTURATO) su "Due Amici"
per tutti e 3 i modelli. Questo produce un output JSON formale comparabile
con l'output della pipeline per sequenza (prompt advanced).
"""
import os, sys, json, datetime, time, re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(ROOT)

from config.prompts import PROMPT_GREIMAS_JSON_STRUTTURATO
from src.providers import get_provider_instance

text_path = os.path.join(ROOT, "data", "inputs", "due_amici_maupassant.txt")
with open(text_path, "r", encoding="utf-8") as f:
    text_content = f.read()

MODELS = [
    "anthropic/claude-sonnet-4.6",
    "google/gemini-2.5-pro",
    "openai/gpt-5.1",
]

timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
output_dir = os.path.join(ROOT, "data", "outputs", f"json_structured_{timestamp}")
os.makedirs(output_dir, exist_ok=True)

print("=" * 60)
print("RUN: Prompt JSON Strutturato su 'Due Amici'")
print(f"Output: {output_dir}")
print("=" * 60)

for model_name in MODELS:
    print(f"\n  Modello: {model_name}...", end=" ", flush=True)
    provider = get_provider_instance("openrouter", model_name)
    
    start = time.time()
    try:
        response = provider.generate(PROMPT_GREIMAS_JSON_STRUTTURATO, text_content, 0.1)
    except Exception as e:
        response = f"ERRORE: {e}"
    elapsed = round(time.time() - start, 2)

    result = {
        "timestamp": datetime.datetime.now().isoformat(),
        "model_provider": "openrouter",
        "model_name": model_name,
        "source_text_file": "due_amici_maupassant.txt",
        "prompt_type": "GREIMAS_JSON_STRUTTURATO",
        "temperature": 0.1,
        "execution_time_seconds": elapsed,
        "response": response
    }

    safe_model = re.sub(r'[\\/*?:"<>|]', "", model_name).replace("/", "_")
    filename = f"{timestamp}_{safe_model}_json_strutturato.json"
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)
    print(f"{elapsed}s")

print(f"\nDONE - 3 file generati in: {output_dir}")
