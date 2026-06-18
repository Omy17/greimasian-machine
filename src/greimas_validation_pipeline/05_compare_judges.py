"""
Fase 5: Comparazione Multi-Judge.

Confronta i risultati di validazione prodotti da due giudici diversi
(es. GPT-4o vs Gemini 2.5 Pro) e calcola metriche di concordanza.

Uso:
  python src/greimas_pipeline/05_compare_judges.py \
    data/outputs/validation_reports \
    data/outputs/validation_reports_gemini \
    --output data/outputs/judge_comparison.json
"""
import os
import sys
import json
import argparse
import math

def load_aggregate(report_dir):
    """Carica _aggregate_scores.json da una cartella di report."""
    path = os.path.join(report_dir, "_aggregate_scores.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Non trovato: {path}")
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_holistic(report_dir):
    """Carica _holistic_aggregate.json dalla sotto-cartella holistic_."""
    # Find holistic subfolder
    for item in os.listdir(report_dir):
        holistic_path = os.path.join(report_dir, item, "_holistic_aggregate.json")
        if os.path.exists(holistic_path):
            with open(holistic_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    return None

def pearson_correlation(x, y):
    """Calcola correlazione di Pearson tra due liste."""
    n = len(x)
    if n < 2:
        return None
    mean_x = sum(x) / n
    mean_y = sum(y) / n
    num = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
    den_x = math.sqrt(sum((xi - mean_x)**2 for xi in x))
    den_y = math.sqrt(sum((yi - mean_y)**2 for yi in y))
    if den_x == 0 or den_y == 0:
        return None
    return num / (den_x * den_y)

def mean_absolute_difference(x, y):
    """Differenza media assoluta tra due liste di punteggi."""
    return sum(abs(xi - yi) for xi, yi in zip(x, y)) / len(x)

def cohens_kappa_ordinal(x, y, k=10):
    """Kappa di Cohen pesato (lineare) per scale ordinali 1-k."""
    n = len(x)
    if n == 0:
        return None
    # Weighted agreement
    total_weight = 0
    expected_weight = 0
    for i in range(n):
        total_weight += 1 - abs(x[i] - y[i]) / (k - 1)
    observed = total_weight / n
    
    # Expected by chance (marginals)
    from collections import Counter
    cx = Counter(x)
    cy = Counter(y)
    for vx in range(1, k+1):
        for vy in range(1, k+1):
            expected_weight += (cx[vx]/n) * (cy[vy]/n) * (1 - abs(vx - vy)/(k-1))
    
    if expected_weight >= 1:
        return None
    return (observed - expected_weight) / (1 - expected_weight)

def compare_local(agg1, agg2):
    """Confronta punteggi di validazione locale tra due giudici."""
    scores1 = agg1["scores"]
    scores2 = agg2["scores"]
    
    # Build lookup: (seq_id, model) -> scores
    def build_lookup(scores):
        lookup = {}
        for s in scores:
            key = (s["sequence_id"], s["model"])
            lookup[key] = s
        return lookup
    
    l1 = build_lookup(scores1)
    l2 = build_lookup(scores2)
    
    common_keys = set(l1.keys()) & set(l2.keys())
    if not common_keys:
        return {"error": "No overlapping entries between the two judge reports."}
    
    dimensions = ["aderenza", "correttezza", "copertura", "originalita", "punteggio_finale"]
    results = {"n_comparisons": len(common_keys), "per_dimension": {}}
    
    for dim in dimensions:
        vals1 = [l1[k][dim] for k in sorted(common_keys) if dim in l1[k]]
        vals2 = [l2[k][dim] for k in sorted(common_keys) if dim in l2[k]]
        
        if not vals1:
            continue
            
        results["per_dimension"][dim] = {
            "mean_judge1": round(sum(vals1)/len(vals1), 2),
            "mean_judge2": round(sum(vals2)/len(vals2), 2),
            "mean_absolute_diff": round(mean_absolute_difference(vals1, vals2), 2),
            "pearson_r": round(pearson_correlation(vals1, vals2), 3) if pearson_correlation(vals1, vals2) else None,
            "weighted_kappa": round(cohens_kappa_ordinal(vals1, vals2), 3) if cohens_kappa_ordinal(vals1, vals2) else None,
        }
    
    # Detail per entry
    details = []
    for k in sorted(common_keys):
        detail = {"sequence_id": k[0], "model": k[1]}
        for dim in dimensions:
            if dim in l1[k] and dim in l2[k]:
                detail[f"{dim}_judge1"] = l1[k][dim]
                detail[f"{dim}_judge2"] = l2[k][dim]
                detail[f"{dim}_diff"] = l2[k][dim] - l1[k][dim]
        details.append(detail)
    results["details"] = details
    
    return results

def compare_holistic(h1, h2):
    """Confronta punteggi olistici tra due giudici."""
    if not h1 or not h2:
        return {"error": "Holistic data missing for one or both judges."}
    
    r1 = {r["model"]: r for r in h1["results"]}
    r2 = {r["model"]: r for r in h2["results"]}
    
    common_models = set(r1.keys()) & set(r2.keys())
    dims = ["coerenza", "completezza", "progressione", "convergenza", "padronanza", "punteggio_olistico_finale"]
    
    results = {"n_models": len(common_models), "per_model": {}}
    for model in sorted(common_models):
        model_cmp = {}
        for dim in dims:
            v1 = r1[model].get(dim)
            v2 = r2[model].get(dim)
            if v1 is not None and v2 is not None:
                model_cmp[dim] = {"judge1": v1, "judge2": v2, "diff": v2 - v1}
        results["per_model"][model] = model_cmp
    
    return results

def main():
    parser = argparse.ArgumentParser(description="Fase 5: Confronto Multi-Judge.")
    parser.add_argument("judge1_dir", help="Cartella report del primo giudice (es. GPT-4o).")
    parser.add_argument("judge2_dir", help="Cartella report del secondo giudice (es. Gemini).")
    parser.add_argument("--judge1-name", default="GPT-4o", help="Nome del primo giudice.")
    parser.add_argument("--judge2-name", default="Gemini-2.5-Pro", help="Nome del secondo giudice.")
    parser.add_argument("--output", default=None, help="File output JSON.")
    args = parser.parse_args()

    print("=" * 60)
    print("FASE 5: Comparazione Multi-Judge")
    print(f"  Giudice 1: {args.judge1_name} ({args.judge1_dir})")
    print(f"  Giudice 2: {args.judge2_name} ({args.judge2_dir})")
    print("=" * 60)

    # Local comparison
    print("\n--- Validazione Locale (per sequenza) ---")
    try:
        agg1 = load_aggregate(args.judge1_dir)
        agg2 = load_aggregate(args.judge2_dir)
        local_cmp = compare_local(agg1, agg2)
        
        print(f"  Confronti: {local_cmp['n_comparisons']}")
        print(f"\n  {'Dimensione':<20} {args.judge1_name:<10} {args.judge2_name:<10} {'MAD':<6} {'Pearson r':<10} {'Kappa':<8}")
        print("  " + "-" * 64)
        for dim, stats in local_cmp["per_dimension"].items():
            print(f"  {dim:<20} {stats['mean_judge1']:<10} {stats['mean_judge2']:<10} "
                  f"{stats['mean_absolute_diff']:<6} {stats['pearson_r'] or 'N/A':<10} "
                  f"{stats['weighted_kappa'] or 'N/A':<8}")
    except FileNotFoundError as e:
        print(f"  ! {e}")
        local_cmp = {"error": str(e)}

    # Holistic comparison
    print("\n--- Validazione Olistica ---")
    try:
        h1 = load_holistic(args.judge1_dir)
        h2 = load_holistic(args.judge2_dir)
        holistic_cmp = compare_holistic(h1, h2)
        
        if "per_model" in holistic_cmp:
            for model, dims in holistic_cmp["per_model"].items():
                model_short = model.split('/')[-1] if '/' in model else model
                print(f"\n  Modello: {model_short}")
                print(f"    {'Dimensione':<30} {args.judge1_name:<10} {args.judge2_name:<10} {'Δ':<5}")
                print("    " + "-" * 55)
                for dim, vals in dims.items():
                    print(f"    {dim:<30} {vals['judge1']:<10} {vals['judge2']:<10} {vals['diff']:+d}")
    except Exception as e:
        print(f"  ! {e}")
        holistic_cmp = {"error": str(e)}

    # Save
    output = {
        "judge1": args.judge1_name,
        "judge2": args.judge2_name,
        "local_comparison": local_cmp,
        "holistic_comparison": holistic_cmp,
    }
    
    out_path = args.output or os.path.join(args.judge1_dir, "_judge_comparison.json")
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n\nReport salvato in: {out_path}")
    print("FASE 5 COMPLETATA.")


if __name__ == "__main__":
    main()
