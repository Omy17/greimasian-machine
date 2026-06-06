import os
import sys
import glob
import json
import datetime
import time
import re

# Add project root to sys.path to allow imports from config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.experiment import MODELS, QUESTIONS, TEMPERATURE, SYSTEM_PROMPT
from src.providers import get_provider_instance

def load_texts():
    texts = {}
    input_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "inputs")
    search_path = os.path.join(input_dir, "*.txt")
    
    files = glob.glob(search_path)
    if not files:
        print(f"Warning: No .txt files found in {input_dir}")
        return texts

    for filepath in files:
        with open(filepath, 'r', encoding='utf-8') as f:
            texts[os.path.basename(filepath)] = f.read()
    return texts

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)

def main():
    print("Starting LLM Comparative Experiment...")
    
    # Setup Output Directory
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(root_dir, "data", "outputs", timestamp)
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Output directory: {output_dir}")

    # Load Texts
    texts = load_texts()
    if not texts:
        print("No texts to process. Exiting.")
        return

    total_iterations = len(texts) * len(MODELS) * len(QUESTIONS)
    current_count = 0
    
    print(f"Texts: {len(texts)}")
    print(f"Models: {len(MODELS)}")
    print(f"Questions: {len(QUESTIONS)}")
    print(f"Total API calls planned: {total_iterations}")
    print("-" * 50)

    for text_name, text_content in texts.items():
        for model_info in MODELS:
            provider_name = model_info["provider"]
            model_name = model_info["model_name"]
            
            # Instantiate Provider
            try:
                provider = get_provider_instance(provider_name, model_name)
            except Exception as e:
                print(f"Skipping model {model_name} ({provider_name}): {e}")
                current_count += len(QUESTIONS) # Skip the count for this model
                continue

            for question in QUESTIONS:
                current_count += 1
                q_id = question["id"]
                q_text = question["text"]
                
                print(f"[{current_count}/{total_iterations}] Processing: {text_name} | {model_name} | {q_id}")
                
                full_user_content = f"Testo da analizzare:\n{text_content}\n\nRichiesta:\n{q_text}"
                
                start_time = time.time()
                try:
                    response = provider.generate(SYSTEM_PROMPT, full_user_content, TEMPERATURE)
                except Exception as e:
                    print(f"  Error generating response: {e}")
                    response = f"ERROR: {str(e)}"
                end_time = time.time()
                
                result = {
                    "timestamp": datetime.datetime.now().isoformat(),
                    "model_provider": provider_name,
                    "model_name": model_name,
                    "text_file": text_name,
                    "question_id": q_id,
                    "question_text": q_text,
                    "system_prompt": SYSTEM_PROMPT,
                    "temperature": TEMPERATURE,
                    "execution_time_seconds": round(end_time - start_time, 2),
                    "input_length": len(full_user_content),
                    "response": response
                }
                
                # Create a filename: model_text_date_question.json
                # Shorten model name and text name if needed
                safe_model = sanitize_filename(model_name)
                safe_text = sanitize_filename(text_name).replace(".txt", "")
                safe_qid = sanitize_filename(q_id)
                
                filename = f"{timestamp}_{safe_model}_{safe_text}_{safe_qid}.json"
                file_path = os.path.join(output_dir, filename)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=4, ensure_ascii=False)
                    
    print("-" * 50)
    print(f"Experiment completed. Results saved in {output_dir}")

if __name__ == "__main__":
    main()
