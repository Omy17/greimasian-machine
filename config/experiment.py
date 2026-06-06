from typing import List, Dict

# System Prompt - Identical for all models
SYSTEM_PROMPT = """Sei un lettore attento. Analizza i testi che ti vengono sottoposti descrivendo come sono costruiti."""

# Generation Parameters
TEMPERATURE = 0.1
MAX_TOKENS = 2000

# Models to test
# Format: {"provider": "openrouter", "model_name": "vendor/model-name"}
MODELS = [
    # Il top per il Quadrato Semiotico (Ragionamento Astratto)
    {"provider": "openrouter", "model_name": "anthropic/claude-sonnet-4.6"},
    {"provider": "openrouter", "model_name": "google/gemini-2.5-pro"}, 
    {"provider": "openrouter", "model_name": "openai/gpt-5.1"},
    # Confronto tra scale testando 3 modelli progressivi: Llama 3.1 8B, Haiku3 e Gemini 2.5 Pro o GPT-4o/5
    #{"provider": "openrouter", "model_name": "meta-llama/llama-3.1-8b-instruct"},
    #{"provider": "openrouter", "model_name": "anthropic/claude-3-haiku"},
    #{"provider": "openrouter", "model_name": "google/gemini-2.5-pro"},
]

# Questions (The 3rd Axis)
QUESTIONS = [

    
    {
        "id": "advanced_greimas",
        "text": "Analizza il seguente testo utilizzando la semiotica strutturale di Greimas."
    }
]
