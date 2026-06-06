"""
Fase 3 (v2): Validazione batch con LLM-Giudice.

Valida tutte le analisi generate in una cartella di Phase 2,
confrontandole con i rispettivi ground truth per sequenza.
Produce un report per ogni file + un report aggregato.
"""
import os
import sys
import json
import argparse
import re
import glob

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.providers import get_provider_instance
from config.experiment import TEMPERATURE

# --- PROMPT PER L'LLM-GIUDICE ---
JUDGE_SYSTEM_PROMPT = """
Sei un professore di semiotica e un giudice imparziale. Il tuo compito è valutare la qualità di un'analisi testuale generata da un modello LLM, confrontandola con un testo di riferimento accademico scritto da A.J. Greimas.

Ti verranno forniti due testi:
1.  **Testo di Riferimento (Ground Truth)**: Un estratto dall'analisi originale di Greimas.
2.  **Testo da Valutare**: L'analisi generata da un modello LLM sullo stesso argomento.

La tua valutazione deve essere rigorosa e basarsi sui seguenti criteri:
1.  **Aderenza Metodologica**: Il testo da valutare utilizza correttamente i concetti e la terminologia di Greimas presenti nel testo di riferimento?
2.  **Correttezza Concettuale**: Le conclusioni a cui arriva il testo da valutare sono coerenti con quelle del testo di riferimento?
3.  **Copertura**: Il testo da valutare copre tutti i punti chiave e le argomentazioni principali presenti nel testo di riferimento?
4.  **Originalità vs. Copia**: Il testo è una rielaborazione intelligente o una semplice parafrasi/copia del testo di riferimento?

Fornisci la tua valutazione ESCLUSIVAMENTE nel seguente formato JSON, e nient'altro:

{
  "punteggio_aderenza_metodologica": <un punteggio intero da 1 a 10>,
  "giustificazione_aderenza": "<una breve giustificazione testuale>",
  "punteggio_correttezza_concettuale": <un punteggio intero da 1 a 10>,
  "giustificazione_correttezza": "<una breve giustificazione testuale>",
  "punteggio_copertura": <un punteggio intero da 1 a 10>,
  "giustificazione_copertura": "<una breve giustificazione testuale>",
  "punteggio_originalita": <un punteggio intero da 1 a 10>,
  "giustificazione_originalita": "<una breve giustificazione testuale>",
  "giudizio_complessivo": "<un paragrafo riassuntivo>",
  "punteggio_finale": <un punteggio complessivo da 1 a 10>
}
"""

# Mapping sequence_id -> ground truth file
GROUND_TRUTH_MAP = {
    "seq_01": "seq_01_sequenza_i.txt",
    "seq_02": "seq_02_sequenza_ii.txt",
    "seq_03": "seq_03_sequenza_iii.txt",
    "seq_04": "seq_04_sequenza_iv.txt",
    "seq_05": "seq_05_sequenza_v.txt",
    "seq_06": "seq_06_sequenza_vi.txt",
    "seq_07": "seq_07_sequenza_vii.txt",
    "seq_08": "seq_08_sequenza_viii.txt",
    "seq_09": "seq_09_sequenza_ix.txt",
    "seq_10": "seq_10_sequenza_x.txt",
    "seq_11": "seq_11_sequenza_xi.txt",
    "seq_12": "seq_12_sequenza_xii.txt",
}


def load_text(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File non trovato: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def extract_sequence_id(filename):
    """Estrae seq_XX dal nome del file."""
    match = re.search(r'(seq_\d{2})', filename)
    return match.group(1) if match else None


def parse_judge_response(response_text):
    """Tenta di parsare il JSON dalla risposta del giudice."""
    # Prova a estrarre JSON da eventuale markdown
    json_match = re.search(r'\{[\s\S]*\}', response_text)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
    return {"raw_response": response_text, "parse_error": True}


def main():
    parser = argparse.ArgumentParser(description="Valida batch di analisi LLM con LLM-Giudice.")
    parser.add_argument("input_dir", help="Cartella contenente i JSON di Phase 2 da validare.")
    parser.add_argument("--judge-model", default="openai/gpt-4o", help="Modello da usare come giudice.")
    args = parser.parse_args()

    print("=" * 60)
    print("FASE 3: Validazione batch con LLM-Giudice")
    print("=" * 60)

    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    gt_dir = os.path.join(base_dir, "data", "ground_truth_chapters")

    # Find all analysis JSON files (exclude _summary.json)
    json_files = sorted([
        f for f in glob.glob(os.path.join(args.input_dir, "*.json"))
        if not os.path.basename(f).startswith("_")
    ])

    if not json_files:
        print(f"Nessun file JSON trovato in: {args.input_dir}")
        sys.exit(1)

    print(f"\nFile da validare: {len(json_files)}")
    print(f"Modello giudice: {args.judge_model}")

    # Setup output
    report_dir = os.path.join(base_dir, "data", "outputs", "validation_reports",
                              os.path.basename(args.input_dir))
    os.makedirs(report_dir, exist_ok=True)
    print(f"Output reports: {report_dir}\n")

    # Init judge
    try:
        judge = get_provider_instance("openrouter", args.judge_model)
    except Exception as e:
        print(f"Errore nell'istanziare il giudice: {e}", file=sys.stderr)
        sys.exit(1)

    all_scores = []

    for i, json_path in enumerate(json_files, 1):
        filename = os.path.basename(json_path)
        print(f"[{i}/{len(json_files)}] Validando: {filename}")

        # Load analysis
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                analysis_data = json.load(f)
            generated_text = analysis_data.get("response", "")
            seq_id = analysis_data.get("sequence_id") or extract_sequence_id(filename)
            model_name = analysis_data.get("model_name", "unknown")
        except Exception as e:
            print(f"  ! Errore caricamento: {e}")
            continue

        # Skip files with error responses
        if generated_text.startswith("Error") or generated_text.startswith("ERRORE"):
            print(f"  ! Risposta con errore, salto.")
            continue

        if not seq_id or seq_id not in GROUND_TRUTH_MAP:
            print(f"  ! Sequenza non riconosciuta: {seq_id}")
            continue

        # Load ground truth
        gt_path = os.path.join(gt_dir, GROUND_TRUTH_MAP[seq_id])
        try:
            ground_truth = load_text(gt_path)
        except FileNotFoundError:
            print(f"  ! Ground truth mancante: {gt_path}")
            continue

        # Call judge
        user_content = f"""
--- TESTO DI RIFERIMENTO (Ground Truth di Greimas) ---
{ground_truth}

--- TESTO DA VALUTARE (Analisi generata da LLM: {model_name}) ---
{generated_text}
"""

        try:
            response = judge.generate(JUDGE_SYSTEM_PROMPT, user_content, TEMPERATURE)
            judgement = parse_judge_response(response)
        except Exception as e:
            print(f"  ! Errore giudice: {e}")
            judgement = {"error": str(e)}

        # Enrich with metadata
        judgement["_meta"] = {
            "source_file": filename,
            "sequence_id": seq_id,
            "model_evaluated": model_name,
            "judge_model": args.judge_model
        }

        # Save individual report
        report_filename = f"validation_{filename}"
        report_path = os.path.join(report_dir, report_filename)
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(judgement, f, indent=2, ensure_ascii=False)

        score = judgement.get("punteggio_finale", "N/A")
        print(f"  -> Punteggio finale: {score}")

        all_scores.append({
            "sequence_id": seq_id,
            "model": model_name,
            "punteggio_finale": judgement.get("punteggio_finale"),
            "aderenza": judgement.get("punteggio_aderenza_metodologica"),
            "correttezza": judgement.get("punteggio_correttezza_concettuale"),
            "copertura": judgement.get("punteggio_copertura"),
            "originalita": judgement.get("punteggio_originalita"),
        })

    # Save aggregate report
    aggregate = {
        "total_validations": len(all_scores),
        "judge_model": args.judge_model,
        "scores": all_scores
    }
    agg_path = os.path.join(report_dir, "_aggregate_scores.json")
    with open(agg_path, 'w', encoding='utf-8') as f:
        json.dump(aggregate, f, indent=2, ensure_ascii=False)

    # Print summary table
    print("\n" + "=" * 60)
    print("RIEPILOGO PUNTEGGI")
    print("=" * 60)
    print(f"{'Sequenza':<10} {'Modello':<30} {'Finale':<8} {'Ader.':<6} {'Corr.':<6} {'Cop.':<6}")
    print("-" * 66)
    for s in all_scores:
        model_short = s['model'].split('/')[-1] if '/' in s['model'] else s['model']
        print(f"{s['sequence_id']:<10} {model_short:<30} {s['punteggio_finale'] or 'N/A':<8} "
              f"{s['aderenza'] or '-':<6} {s['correttezza'] or '-':<6} {s['copertura'] or '-':<6}")

    print(f"\nReport aggregato: {agg_path}")
    print("FASE 3 COMPLETATA.")


if __name__ == "__main__":
    main()
