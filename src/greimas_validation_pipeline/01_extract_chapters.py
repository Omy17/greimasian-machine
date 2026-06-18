
import os
import re
import pdfplumber

def sanitize_filename(name):
    """Rimuove i caratteri non validi e accorcia il nome del file."""
    # Sostituisce gli spazi e i caratteri speciali con underscore
    s_name = re.sub(r'[\s\W]+', '_', name.lower())
    # Rimuove eventuali underscore iniziali o finali
    return s_name.strip('_')

def extract_chapters_from_pdf(pdf_path, output_dir, chapter_delimiters):
    """
    Estrae il testo da un PDF e lo divide in file di testo basati su delimitatori di capitolo.

    Args:
        pdf_path (str): Percorso del file PDF.
        output_dir (str): Directory dove salvare i file di testo dei capitoli.
        chapter_delimiters (list): Lista di stringhe che segnano l'inizio di ogni capitolo.
    """
    if not os.path.exists(pdf_path):
        print(f"Errore: File PDF non trovato a '{pdf_path}'")
        return

    os.makedirs(output_dir, exist_ok=True)
    print(f"Directory di output: '{output_dir}'")

    with pdfplumber.open(pdf_path) as pdf:
        full_text_pages = [page.extract_text() for page in pdf.pages if page.extract_text()]

    current_chapter_index = -1
    current_chapter_text = ""
    
    # Aggiungiamo un delimitatore finale fittizio per salvare l'ultimo capitolo
    delimiters_with_end = chapter_delimiters + ["END_OF_BOOK_DELIMITER"]

    # Troviamo le posizioni di tutti i delimitatori nel testo
    # Questo è un approccio semplificato. Un PDF reale potrebbe richiedere una logica più complessa
    # per trovare le pagine e le posizioni esatte.
    
    chapter_content = {i: "" for i in range(len(chapter_delimiters))}
    active_chapter = -1

    for page_text in full_text_pages:
        # Controlla se un nuovo capitolo inizia in questa pagina
        found_new_chapter = False
        for i, title in enumerate(chapter_delimiters):
            # Usiamo una regex case-insensitive per trovare il titolo
            if re.search(r'\b' + re.escape(title) + r'\b', page_text, re.IGNORECASE):
                active_chapter = i
                found_new_chapter = True
                print(f"Trovato l'inizio del capitolo {i+1}: '{title}'")
                break # Trovato il primo titolo possibile nella pagina

        if active_chapter != -1:
            chapter_content[active_chapter] += page_text + "\n"

    # Salvataggio dei capitoli estratti
    for i, title in enumerate(chapter_delimiters):
        content = chapter_content.get(i)
        if content:
            # Pulisce il contenuto rimuovendo il titolo del capitolo successivo se presente
            if i + 1 < len(chapter_delimiters):
                next_title = chapter_delimiters[i+1]
                # Cerca il titolo successivo e taglia tutto ciò che viene dopo
                match = re.search(r'\b' + re.escape(next_title) + r'\b', content, re.IGNORECASE)
                if match:
                    content = content[:match.start()]

            filename = f"seq_{i+1:02d}_{sanitize_filename(title)}.txt"
            filepath = os.path.join(output_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content.strip())
            print(f"Capitolo salvato in: {filename}")
        else:
            print(f"Attenzione: Nessun contenuto trovato per il capitolo {i+1}: '{title}'")


def main():
    """Funzione principale per orchestrare l'estrazione."""
    print("Avvio Fase 1: Estrazione dei capitoli dal PDF di Greimas...")

    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    pdf_path = os.path.join(base_dir, "data", "inputs", "GREIMAS MAUPASSANT (Italiano).pdf")
    output_dir = os.path.join(base_dir, "data", "ground_truth_chapters")

    # Definiamo i titoli delle sequenze come appaiono nell'indice
    # Questi sono i "delimitatori" che useremo per dividere il testo.
    # L'accuratezza di queste stringhe è FONDAMENTALE.
    chapter_titles = [
        "SEQUENZA I\nParigi",
        "SEQUENZA II\nL’amicizia",
        "SEQUENZA III\nLa passeggiata",
        "SEQUENZA IV\nLa ricerca",
        "SEQUENZA V\nLa pace",
        "SEQUENZA VI\nLa guerra",
        "SEQUENZA VII\nLa cattura",
        "SEQUENZA VIII\nLa reinterpretazione",
        "SEQUENZA IX\nIl rifiuto",
        "SEQUENZA X\nLa morte",
        "SEQUENZA XI\nLe esequie",
        "SEQUENZA XII\nLa chiusura del racconto"
    ]
    
    # Semplifichiamo i titoli per la ricerca, cercando solo la parte "SEQUENZA X"
    simple_chapter_titles = [f"SEQUENZA {roman}" for roman in ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"]]


    extract_chapters_from_pdf(pdf_path, output_dir, simple_chapter_titles)

    print("\nEstrazione completata.")
    print(f"Controlla la cartella '{output_dir}' per verificare i file generati.")

if __name__ == "__main__":
    main()
