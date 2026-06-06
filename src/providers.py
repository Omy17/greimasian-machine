import os
import abc
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LLMProvider(abc.ABC):
    def __init__(self, model_name: str):
        self.model_name = model_name

    @abc.abstractmethod
    def generate(self, system_prompt: str, full_user_content: str, temperature: float) -> str:
        """
        Generates a response from the LLM.
        """
        pass

class OpenRouterProvider(LLMProvider):
    def __init__(self, model_name: str):
        super().__init__(model_name)
        try:
            from openai import OpenAI
            api_key = os.getenv("OPENROUTER_API_KEY")
            if not api_key:
                raise ValueError("OPENROUTER_API_KEY not found in environment variables")
            import httpx
            self.client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key,
                timeout=httpx.Timeout(300.0, connect=30.0),
            )
        except ImportError:
            raise ImportError("OpenAI library not installed. Please run `pip install openai`")

    def generate(self, system_prompt: str, full_user_content: str, temperature: float, max_retries: int = 3) -> str:
        import time as _time
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": full_user_content}
                    ],
                    temperature=temperature,
                )
                content = response.choices[0].message.content
                if content is None:
                    if attempt < max_retries - 1:
                        _time.sleep(5)
                        continue
                    return "Error: model returned empty response after retries"
                return content
            except Exception as e:
                if attempt < max_retries - 1:
                    _time.sleep(10)
                    continue
                return f"Error gathering response from OpenRouter: {str(e)}"

def get_provider_instance(provider_name: str, model_name: str) -> LLMProvider:
    if provider_name.lower() == "openrouter":
        return OpenRouterProvider(model_name)
    else:
        # Fallback for direct providers if still needed, but currently fully switched to OpenRouter
        raise ValueError(f"Unknown provider: {provider_name}. Only 'openrouter' is currently supported.")
