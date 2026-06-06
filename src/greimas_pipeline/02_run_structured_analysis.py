"""
Fase 2 (v2): Generazione delle analisi strutturate per TUTTE le 12 sequenze × 3 modelli.

Produce 36 file JSON (12 sequenze × 3 modelli) in una cartella timestamped.
"""
import os
import sys
import json
import datetime
import time
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.experiment import MODELS, TEMPERATURE
from config.greimas_prompts_sequences import get_system_prompt_for_sequence, get_all_sequence_ids, SEQUENCE_PROMPTS
from src.providers import get_provider_instance


def load_source_text(base_dir):
    """Carica il testo del racconto 'Due Amici'."""
    text_path = os.path.join(base_dir, "data", "inputs", "due_amici_maupassant.txt")
    if not os.path.exists(text_path):
        raise FileNotFoundError(f"Testo sorgente non trovato: {text_path}")
    with open(text_path, 'r', encoding='utf-8') as f:
        return f.read()


def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name).replace("/", "_")


def main():
    print("=" * 60)
    print("FASE 2: Generazione analisi strutturate (12 sequenze x 3 modelli)")
    print("=" * 60)

    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # Setup output directory
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(base_dir, "data", "outputs", f"structured_analysis_{timestamp}")
    os.makedirs(output_dir, exist_ok=True)
    print(f"\nOutput directory: {output_dir}")

    # Load source text
    try:
        text_content = load_source_text(base_dir)
        print("Testo 'Due Amici' caricato correttamente.\n")
    except FileNotFoundError as e:
        print(f"Errore: {e}", file=sys.stderr)
        sys.exit(1)

    sequence_ids = get_all_sequence_ids()
    total = len(sequence_ids) * len(MODELS)
    current = 0
    results_summary = []

    print(f"Combinazioni totali: {len(sequence_ids)} sequenze x {len(MODELS)} modelli = {total}")
    print("-" * 60)

    for seq_id in sequence_ids:
        seq_title = SEQUENCE_PROMPTS[seq_id]["title"]
        system_prompt = get_system_prompt_for_sequence(seq_id)

        for model_info in MODELS:
            current += 1
            provider_name = model_info["provider"]
            model_name = model_info["model_name"]

            print(f"[{current}/{total}] {seq_title} -- {model_name}")

            try:
                provider = get_provider_instance(provider_name, model_name)
            except Exception as e:
                print(f"  ! Errore provider: {e}")
                continue

            user_content = (
                f"Analizza ESCLUSIVAMENTE la porzione del racconto corrispondente a: {seq_title}\n\n"
                f"Ecco il testo COMPLETO del racconto \"Due amici\" di Maupassant:\n\n---\n{text_content}\n---"
            )

            start_time = time.time()
            try:
                response = provider.generate(system_prompt, user_content, TEMPERATURE)
            except Exception as e:
                print(f"  ! Errore generazione: {e}")
                response = f"ERRORE: {str(e)}"
            elapsed = round(time.time() - start_time, 2)

            result = {
                "timestamp": datetime.datetime.now().isoformat(),
                "model_provider": provider_name,
                "model_name": model_name,
                "sequence_id": seq_id,
                "sequence_title": seq_title,
                "source_text_file": "due_amici_maupassant.txt",
                "prompt_skill": "GREIMAS_STRUCTURED_ANALYSIS_BY_SEQUENCE",
                "temperature": TEMPERATURE,
                "execution_time_seconds": elapsed,
                "response": response
            }

            safe_model = sanitize_filename(model_name)
            filename = f"{timestamp}_{seq_id}_{safe_model}.json"
            file_path = os.path.join(output_dir, filename)

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=4, ensure_ascii=False)

            print(f"  -> Completato in {elapsed}s -> {filename}")
            results_summary.append({
                "sequence": seq_id,
                "model": model_name,
                "time": elapsed,
                "file": filename
            })

    # Save summary
    summary_path = os.path.join(output_dir, "_summary.json")
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": timestamp,
            "total_analyses": len(results_summary),
            "models": [m["model_name"] for m in MODELS],
            "sequences": sequence_ids,
            "results": results_summary
        }, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 60)
    print(f"FASE 2 COMPLETATA: {len(results_summary)}/{total} analisi generate.")
    print(f"Summary: {summary_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
