# Guida alla Validazione dell'Analisi Semiotica

Questa guida descrive i passaggi necessari per eseguire la pipeline di analisi semiotica e validare i risultati generati da un modello LLM rispetto a un testo di riferimento di A.J. Greimas.

## Prerequisiti

Assicurati di avere un ambiente virtuale Python configurato e le dipendenze installate.

1.  **Attiva l'ambiente virtuale**:
    ```bash
    .\.venv\Scripts\Activate.ps1
    ```

## Passaggi per la Validazione

La pipeline è composta da 3 fasi principali.

### Fase 1: Estrazione delle Sequenze (Opzionale)

Questo passaggio è necessario solo se il testo di input non è già suddiviso in capitoli o sequenze. Lo script `01_extract_chapters.py` divide un testo lungo in file di testo separati, uno per ogni sequenza.

1.  **Esegui lo script**:
    ```bash
    python src/greimas_pipeline/01_extract_chapters.py "data/inputs/due_amici_maupassant.txt" "data/outputs/due_amici_chapters"
    ```
    - Il primo argomento è il percorso del file di testo di input.
    - Il secondo argomento è la directory di output dove verranno salvati i file delle sequenze.

### Fase 2: Esecuzione dell'Analisi Strutturata

Questo script prende una sequenza (un file di testo) e utilizza un modello LLM per generare un'analisi semiotica strutturata in formato JSON.

1.  **Esegui lo script**:
    ```bash
    python src/greimas_pipeline/02_run_structured_analysis.py "data/outputs/due_amici_chapters/seq_01.txt" "openrouter/google/gemini-pro" "data/outputs/structured_analysis"
    ```
    - Il primo argomento è il percorso del file di testo della sequenza da analizzare.
    - Il secondo argomento è il nome del modello LLM da utilizzare (es. `openrouter/google/gemini-pro`, `anthropic/claude-3.5-sonnet`, ecc.).
    - Il terzo argomento è la directory di output dove verrà salvato il file JSON con l'analisi.

Il file di output avrà un nome simile a `structured_analysis_20260508_103000_google-gemini-pro.json`.

### Fase 3: Validazione con LLM-Giudice

Questo script finale confronta l'analisi generata dall'LLM (il file JSON della Fase 2) con il testo di riferimento "ground truth" di Greimas. Utilizza un altro LLM come "giudice" per valutare la qualità dell'analisi.

1.  **Esegui lo script**:
    ```bash
    python src/greimas_pipeline/03_validate_analysis.py "data/outputs/structured_analysis/structured_analysis_20260508_103000_google-gemini-pro.json"
    ```
    - L'unico argomento è il percorso del file JSON generato nella Fase 2.

2.  **Controlla l'output**:
    Lo script eseguirà la validazione e salverà un nuovo file JSON con il giudizio nella cartella `data/outputs/validation_reports/`. Il nome del file includerà la data e il modello utilizzato, ad esempio: `validation_20260508_103100_google-gemini-pro_structured_analysis.json`.

    Questo file conterrà i punteggi e le giustificazioni per l'aderenza metodologica, la correttezza concettuale e la copertura, oltre a un giudizio complessivo.
