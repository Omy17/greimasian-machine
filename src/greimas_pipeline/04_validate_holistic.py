"""
Fase 4: Validazione Olistica — Coerenza globale dell'analisi del racconto.

Per ciascun modello, concatena le 12 analisi di sequenza e valuta:
- Coerenza inter-sequenziale (stabilità attanti/ruoli tra sequenze)
- Completezza strutturale (tutti i programmi narrativi principali identificati)
- Progressione narrativa (trasformazioni correttamente ordinate)
- Convergenza finale (sanzione coerente con contratto iniziale)

Confronta con il ground truth completo (tutte le 12 sequenze concatenate).
"""
import os
import sys
import json
import glob
import argparse
import re
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.providers import get_provider_instance
from config.experiment import TEMPERATURE

HOLISTIC_JUDGE_PROMPT = """
Sei un professore di semiotica strutturale esperto nel metodo di Greimas. Il tuo compito è valutare la COERENZA GLOBALE di un'analisi semiotica completa di un racconto, composta da 12 sequenze generate da un modello LLM.

Ti verranno forniti:
1. **Ground Truth completo**: L'analisi originale di Greimas su tutte le 12 sequenze del racconto "Due amici" di Maupassant.
2. **Analisi completa generata**: Le 12 sequenze di analisi prodotte dal modello LLM, concatenate in ordine.

Valuta l'analisi generata sui seguenti criteri OLISTICI (non per singola sequenza, ma come opera complessiva):

1. **Coerenza inter-sequenziale** (1-10): I nomi degli attanti, i ruoli tematici e le isotopie sono stabili e coerenti tra una sequenza e l'altra? Il modello mantiene una visione unitaria?

2. **Completezza strutturale** (1-10): Il modello ha identificato TUTTI i programmi narrativi principali del racconto (PN del soggetto, PN dell'anti-soggetto, schema narrativo canonico completo)?

3. **Progressione narrativa** (1-10): Le trasformazioni di stato sono correttamente ordinate e concatenate? Il percorso generativo del senso è rispettato dal livello profondo a quello di superficie?

4. **Convergenza finale** (1-10): La sanzione finale (Sequenze X-XII) è coerente con il contratto iniziale (Sequenze I-III)? Il modello coglie l'arco narrativo complessivo?

5. **Padronanza terminologica globale** (1-10): Il modello usa la terminologia greimasiana in modo consistente e corretto nell'arco di tutta l'analisi?

Fornisci la tua valutazione ESCLUSIVAMENTE nel seguente formato JSON:

{
  "punteggio_coerenza_intersequenziale": <1-10>,
  "giustificazione_coerenza": "<spiegazione dettagliata con esempi>",
  "punteggio_completezza_strutturale": <1-10>,
  "giustificazione_completezza": "<quali PN sono stati identificati e quali mancano>",
  "punteggio_progressione_narrativa": <1-10>,
  "giustificazione_progressione": "<spiegazione con riferimenti alle sequenze>",
  "punteggio_convergenza_finale": <1-10>,
  "giustificazione_convergenza": "<come il modello gestisce l'arco contratto-sanzione>",
  "punteggio_padronanza_terminologica": <1-10>,
  "giustificazione_padronanza": "<coerenza nell'uso del lessico tecnico>",
  "punteggio_olistico_finale": <1-10>,
  "giudizio_complessivo": "<paragrafo di sintesi critica sulla capacità del modello di produrre un'analisi globalmente coerente>",
  "punti_di_forza": ["<punto 1>", "<punto 2>", "..."],
  "punti_di_debolezza": ["<punto 1>", "<punto 2>", "..."]
}
"""


def load_ground_truth_full(base_dir):
    """Carica e concatena tutti i 12 file di ground truth."""
    gt_dir = os.path.join(base_dir, "data", "ground_truth_chapters")
    full_text = []
    for i in range(1, 13):
        filename = f"seq_{i:02d}_sequenza_{'i' * i if i <= 3 else ['iv','v','vi','vii','viii','ix','x','xi','xii'][i-4]}.txt"
        # Use actual filenames from directory
        pattern = os.path.join(gt_dir, f"seq_{i:02d}_*.txt")
        matches = glob.glob(pattern)
        if matches:
            with open(matches[0], 'r', encoding='utf-8') as f:
                full_text.append(f"{'='*40}\n{f.read()}")
    return "\n\n".join(full_text)


def collect_model_analyses(input_dir, model_name):
    """Raccoglie e concatena le 12 analisi di un modello in ordine."""
    analyses = []
    for i in range(1, 13):
        seq_id = f"seq_{i:02d}"
        # Find file matching this sequence and model
        pattern = os.path.join(input_dir, f"*{seq_id}*")
        for filepath in sorted(glob.glob(pattern)):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if model_name in data.get("model_name", ""):
                    analyses.append({
                        "sequence_id": seq_id,
                        "response": data.get("response", "")
                    })
                    break
            except (json.JSONDecodeError, KeyError):
                continue
    return analyses


def parse_judge_response(response_text):
    """Tenta di parsare il JSON dalla risposta del giudice."""
    json_match = re.search(r'\{[\s\S]*\}', response_text)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
    return {"raw_response": response_text, "parse_error": True}


def main():
    parser = argparse.ArgumentParser(description="Fase 4: Validazione olistica dell'analisi completa.")
    parser.add_argument("input_dir", help="Cartella contenente i JSON di Phase 2.")
    parser.add_argument("--judge-model", default="openai/gpt-4o", help="Modello giudice.")
    args = parser.parse_args()

    print("=" * 60)
    print("FASE 4: Validazione Olistica (coerenza globale per modello)")
    print("=" * 60)

    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # Load full ground truth
    print("\nCaricamento ground truth completo (12 sequenze)...")
    ground_truth_full = load_ground_truth_full(base_dir)
    print(f"  Ground truth: {len(ground_truth_full)} caratteri")

    # Identify models from the input directory
    json_files = [f for f in glob.glob(os.path.join(args.input_dir, "*.json"))
                  if not os.path.basename(f).startswith("_")]
    models_found = set()
    for jf in json_files:
        try:
            with open(jf, 'r', encoding='utf-8') as f:
                data = json.load(f)
            models_found.add(data.get("model_name", ""))
        except:
            continue

    models_found = sorted(m for m in models_found if m)
    print(f"  Modelli trovati: {models_found}")

    # Init judge
    try:
        judge = get_provider_instance("openrouter", args.judge_model)
    except Exception as e:
        print(f"Errore giudice: {e}", file=sys.stderr)
        sys.exit(1)

    # Output directory
    report_dir = os.path.join(base_dir, "data", "outputs", "validation_reports",
                              "holistic_" + os.path.basename(args.input_dir))
    os.makedirs(report_dir, exist_ok=True)

    holistic_results = []

    for model_name in models_found:
        print(f"\n{'─' * 40}")
        print(f"Validazione olistica: {model_name}")
        print(f"{'─' * 40}")

        # Collect all 12 analyses for this model
        analyses = collect_model_analyses(args.input_dir, model_name)
        print(f"  Sequenze trovate: {len(analyses)}/12")

        if len(analyses) < 6:
            print(f"  ! Troppo poche sequenze ({len(analyses)}), salto.")
            continue

        # Concatenate
        full_analysis = "\n\n".join([
            f"{'='*40}\n{a['sequence_id'].upper()}\n{'='*40}\n{a['response']}"
            for a in analyses
        ])
        print(f"  Analisi concatenata: {len(full_analysis)} caratteri")

        # Build judge prompt (we may need to truncate if too long)
        # Ground truth can be very long — we send a summary instruction
        user_content = f"""
--- GROUND TRUTH COMPLETO (Analisi originale di Greimas, 12 sequenze) ---
{ground_truth_full[:80000]}

--- ANALISI COMPLETA GENERATA DA: {model_name} ({len(analyses)} sequenze) ---
{full_analysis[:80000]}
"""

        print(f"  Invocazione giudice olistico...")
        start = time.time()
        try:
            response = judge.generate(HOLISTIC_JUDGE_PROMPT, user_content, TEMPERATURE)
            judgement = parse_judge_response(response)
        except Exception as e:
            print(f"  ! Errore: {e}")
            judgement = {"error": str(e)}
        elapsed = round(time.time() - start, 2)

        judgement["_meta"] = {
            "model_evaluated": model_name,
            "judge_model": args.judge_model,
            "sequences_count": len(analyses),
            "evaluation_time_seconds": elapsed
        }

        # Save
        safe_model = re.sub(r'[\\/*?:"<>|]', "", model_name).replace("/", "_")
        report_path = os.path.join(report_dir, f"holistic_{safe_model}.json")
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(judgement, f, indent=2, ensure_ascii=False)

        score = judgement.get("punteggio_olistico_finale", "N/A")
        print(f"  -> Punteggio olistico finale: {score} (in {elapsed}s)")

        holistic_results.append({
            "model": model_name,
            "punteggio_olistico_finale": judgement.get("punteggio_olistico_finale"),
            "coerenza": judgement.get("punteggio_coerenza_intersequenziale"),
            "completezza": judgement.get("punteggio_completezza_strutturale"),
            "progressione": judgement.get("punteggio_progressione_narrativa"),
            "convergenza": judgement.get("punteggio_convergenza_finale"),
            "padronanza": judgement.get("punteggio_padronanza_terminologica"),
        })

    # Save aggregate
    agg_path = os.path.join(report_dir, "_holistic_aggregate.json")
    with open(agg_path, 'w', encoding='utf-8') as f:
        json.dump({"results": holistic_results}, f, indent=2, ensure_ascii=False)

    # Print summary
    print("\n" + "=" * 60)
    print("RIEPILOGO VALIDAZIONE OLISTICA")
    print("=" * 60)
    print(f"{'Modello':<35} {'Olistico':<9} {'Coer.':<6} {'Compl.':<7} {'Progr.':<7} {'Conv.':<6} {'Padr.':<6}")
    print("-" * 76)
    for r in holistic_results:
        model_short = r['model'].split('/')[-1] if '/' in r['model'] else r['model']
        print(f"{model_short:<35} {r['punteggio_olistico_finale'] or 'N/A':<9} "
              f"{r['coerenza'] or '-':<6} {r['completezza'] or '-':<7} "
              f"{r['progressione'] or '-':<7} {r['convergenza'] or '-':<6} {r['padronanza'] or '-':<6}")

    print(f"\nReport salvati in: {report_dir}")
    print("FASE 4 COMPLETATA.")


if __name__ == "__main__":
    main()
