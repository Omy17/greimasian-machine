# -*- coding: utf-8 -*-
"""
Prompt strutturati per ciascuna delle 12 sequenze dell'analisi greimasiana
di "Due Amici" di Maupassant.

Ogni prompt richiede al modello di seguire esattamente la struttura del ground truth
di Greimas per la sequenza corrispondente.
"""

SYSTEM_PROMPT_BASE = """
Sei un esperto di semiotica strutturale specializzato nel metodo di Algirdas Julien Greimas.
Il tuo compito è analizzare il testo fornito, "Due amici" di Guy de Maupassant, seguendo in modo rigoroso e dettagliato la struttura dell'analisi indicata.

Produci un'analisi completa e ben strutturata. Per ogni punto dell'indice fornito, elabora un paragrafo di analisi pertinente, basandoti esclusivamente sul testo del racconto. Mantieni la stessa numerazione e gli stessi titoli dell'indice.

Concentrati ESCLUSIVAMENTE sulla sequenza indicata, analizzando il segmento testuale corrispondente con la massima profondità semiotica.
"""

# Mapping: sequence_id -> (titolo, struttura delle sezioni)
SEQUENCE_PROMPTS = {
    "seq_01": {
        "title": "SEQUENZA I: Parigi",
        "structure": """
### SEQUENZA I: Parigi
1.  **Organizzazione testuale**
    1.1. Disgiunzioni temporali e spaziali (La temporalità, La spazialità)
    1.2. Disgiunzione attoriale
2.  **La prima frase**
    2.1. I ruoli tematici
    2.2. Le strutture aspettuali
    2.3. Una logica delle approssimazioni
3.  **La seconda frase**
    3.1. L'isotopia discorsiva
    3.2. La rappresentazione spaziale
    3.3. L'esplicitazione semantica
    3.4. Gli investimenti assiologici
4.  **La terza frase**
    4.1. La figura spaziale di Parigi
    4.2. Verso l'abolizione del senso
5.  **Osservazioni finali**
"""
    },
    "seq_02": {
        "title": "SEQUENZA II: L'amicizia",
        "structure": """
### SEQUENZA II: L'amicizia
1.  **La sequenza e il suo contesto**
    1.1. Una sequenza intercalare
    1.2. La linearità del discorso
2.  **L'organizzazione interna della sequenza**
    2.1. Organizzazione paradigmatica
    2.2. Organizzazione sintagmatica
3.  **Il fare euforico**
    3.1. Il programma discorsivo
    3.2. La valorizzazione del programma
    3.3. L'installazione dell'attante duale
4.  **L'universo figurativo dei valori**
    4.1. Il riconoscimento dei valori
    4.2. Le trasfigurazioni del Sole
    4.3. La nebbia acquatica
    4.4. La nebbia celeste
    4.5. Il sangue solare
    4.6. L'apparire del Cielo
    4.7. Il quadrato semiotico
"""
    },
    "seq_03": {
        "title": "SEQUENZA III: La passeggiata",
        "structure": """
### SEQUENZA III: La passeggiata
1.  **Lo statuto e l'organizzazione della sequenza**
    1.1. La delimitazione spazio-temporale
    1.2. La passeggiata
    1.3. Camminare e fermarsi
2.  **L'avvenire dell'evento**
    2.1. Temporalizzazione e aspettualizzazione
    2.2. La focalizzazione dell'attore-soggetto
    2.3. L'innesco della narrazione
3.  **La ricostituzione dell'attante**
    3.1. Il riconoscimento
    3.2. La rimpatriata
    3.3. La virtualizzazione e l'attualizzazione dei contenuti
    3.4. L'instaurazione dell'illusione
4.  **La competenza del soggetto**
    4.1. L'attualizzazione del voler-fare
    4.2. Un poter-fare illusorio
    4.3. I trickster
    4.4. Le due figure del trickster
    4.5. Il non-destinante
    4.6. Il passaggio all'atto
"""
    },
    "seq_04": {
        "title": "SEQUENZA IV: La ricerca",
        "structure": """
### SEQUENZA IV: La ricerca
1.  **Segmentazione provvisoria**
2.  **Lo spazio familiare**
    2.1. Il lasciapassare
    2.2. L'organizzazione spaziale del racconto
3.  **Lo spazio topico**
    3.1. Nuova segmentazione
    3.2. Fermata interpretativa
    3.3. Lo spostamento persuasivo
"""
    },
    "seq_05": {
        "title": "SEQUENZA V: La pace",
        "structure": """
### SEQUENZA V: La pace
1.  **Problemi di segmentazione**
2.  **La costruzione dello spazio cognitivo**
    2.1. La ricerca della solitudine
    2.2. L'assenza dell'anti-soggetto
3.  **La performanza dell'eroe**
    3.1. Analisi testuale e narrativa
    3.2. Analisi semantica
"""
    },
    "seq_06": {
        "title": "SEQUENZA VI: La guerra",
        "structure": """
### SEQUENZA VI: La guerra
1.  **Organizzazione testuale**
2.  **Il Mont-Valérien**
    2.1. Il rumore e il silenzio
    2.2. La figura antropomorfa
    2.3. L'universo sociolettale e l'universo idiolettale
    2.4. Il fare mortale
3.  **La morte e la libertà**
    3.1. La segmentazione
    3.2. "Peggio delle bestie"
    3.3. Natura e cultura
    3.4. Il proto-destinante sociale
    3.5. "Mai si sarebbe stati liberi"
    3.6. Il perno narrativo
    3.7. La presenza della morte
"""
    },
    "seq_07": {
        "title": "SEQUENZA VII: La cattura",
        "structure": """
### SEQUENZA VII: La cattura
1.  **Organizzazione testuale**
    1.1. Delimitazione della sequenza
    1.2. Articolazione interna
2.  **La dimensione pragmatica**
    2.1. Il programma narrativo dell'anti-soggetto
    2.2. Gli oggetti di valore: O₁
    2.3. Gli oggetti di valore: O₂
    2.4. Soggetto secondo il fare e soggetto secondo l'essere
    2.5. Struttura dell'anti-soggetto
3.  **La dimensione cognitiva**
    3.1. Il "punto di vista"
    3.2. Il doppio riconoscimento
    3.3. La presa di parola
"""
    },
    "seq_08": {
        "title": "SEQUENZA VIII: La reinterpretazione",
        "structure": """
### SEQUENZA VIII: La reinterpretazione
1.  **Organizzazione testuale**
    1.1. Delimitazione della sequenza
    1.2. Articolazione interna
2.  **Installazione del discorso**
    2.1. Procedure retoriche
    2.2. Preparativi d'enunciazione
3.  **Il discorso al secondo grado**
    3.1. La contro-lettura
    3.2. La lettura del PN di S
    3.3. L'interpretazione e il canone
    3.4. Ritorno all'interpretazione
    3.5. Ruoli e percorsi tematici
    3.6. La rivelazione del segreto
    3.7. Il trasferimento delle responsabilità
    3.8. L'ideologia del dominio
    3.9. L'enunciazione informativa
"""
    },
    "seq_09": {
        "title": "SEQUENZA IX: Il rifiuto",
        "structure": """
### SEQUENZA IX: Il rifiuto
1.  **Organizzazione testuale**
    1.1. Delimitazione della sequenza
    1.2. Articolazione interna
2.  **Il programma narrativo dell'anti-soggetto**
    2.1. La competenza narrativa
    2.2. La performanza narrativa
3.  **Il programma narrativo del soggetto**
    3.1. L'interpretazione dei valori offerti
    3.2. L'interpretazione del contro-valore richiesto
    3.3. Il programma narrativo della liberazione
"""
    },
    "seq_10": {
        "title": "SEQUENZA X: La morte",
        "structure": """
### SEQUENZA X: La morte
1.  **Organizzazione testuale**
    1.1. Delimitazione della sequenza
    1.2. Articolazione interna
2.  **L'economia della sequenza**
    2.1. L'isotopia patriottica
    2.2. La messinscena
3.  **L'ultimo tentativo**
    3.1. L'intimazione
    3.2. La mancata separazione
4.  **Gli addii**
    4.1. La rete paradigmatica
    4.2. La comparazione dei valori
    4.3. La ricostituzione dell'attante duale
5.  **Il martirio**
    5.1. L'ultimo scontro
    5.2. La vacuità del Cielo
    5.3. La parabola cristiana
"""
    },
    "seq_11": {
        "title": "SEQUENZA XI: Le esequie",
        "structure": """
### SEQUENZA XI: Le esequie
1.  **Organizzazione testuale**
    1.1. Delimitazione della sequenza
    1.2. Articolazione interna
2.  **La trasfigurazione**
    2.1. La procedura dell'occultamento
    2.2. L'immersione
3.  **Il riconoscimento**
    3.1. Le manifestazioni dell'Acqua
    3.2. "Un po' di sangue galleggiava"
4.  **L'orazione funebre**
    4.1. L'assiologia dell'anti-soggetto
    4.2. L'ideologia del potere
    4.3. La ridistribuzione del sapere
5.  **Il martirio**
"""
    },
    "seq_12": {
        "title": "SEQUENZA XII: La chiusura del racconto",
        "structure": """
### SEQUENZA XII: La chiusura del racconto
1.  **Organizzazione testuale**
    1.1. Delimitazione della sequenza
    1.2. Articolazione interna
2.  **Il consumo dei pesci**
    2.1. Un'esperienza "deliziosa"
    2.2. Il fare cognitivo
    2.3. Il fare pragmatico
    2.4. La ripresa dell'isotopia cristiana
3.  **La consunzione dell'evento**
"""
    },
}


def get_system_prompt_for_sequence(seq_id: str) -> str:
    """
    Costruisce il system prompt completo per una data sequenza.
    """
    seq = SEQUENCE_PROMPTS[seq_id]
    return f"""{SYSTEM_PROMPT_BASE}

Ecco la struttura che la tua analisi deve seguire OBBLIGATORIAMENTE:

---

{seq['structure']}
"""


def get_all_sequence_ids() -> list:
    """Ritorna la lista ordinata degli ID delle sequenze."""
    return sorted(SEQUENCE_PROMPTS.keys())
