import requests
import yaml
from pathlib import Path

CONFIG_PATH = Path("config/llm_config.yaml")

class LLMBridge:
    def __init__(self):
        self.config = self.load_config()

    def load_config(self):
        if CONFIG_PATH.exists():
            return yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
        return {}

    def send(self, prompt: str) -> str:
        provider = self.config.get("provider", "ollama")
        model = self.config.get("model", "codellama:7b-instruct")
        temperature = self.config.get("temperature", 0.2)
        max_tokens = self.config.get("max_tokens", 1024)

        if provider == "ollama":
            url = "http://localhost:11434/api/generate"
            data = {
                "model": model,
                "prompt": prompt,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": False
            }
            response = requests.post(url, json=data)
            return response.json().get("response", "").strip()

        elif provider == "lmstudio":
            url = "http://localhost:1234/v1/chat/completions"
            data = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            response = requests.post(url, json=data)
            return response.json()["choices"][0]["message"]["content"].strip()

        else:
            raise ValueError(f"Provider '{provider}' not supported.")