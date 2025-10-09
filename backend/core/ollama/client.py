import requests
import json
from typing import Optional
from ..config import OLLAMA_URL, OLLAMA_MODEL, OLLAMA_FALLBACK_MODEL, OLLAMA_BACKUP_MODEL, CLASSIFY_PROMPT, OLLAMA_TIMEOUT

def test_ollama_connection() -> bool:
    """Проверяет подключение к Ollama."""
    try:
        response = requests.get("http://localhost:11434/api/version", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def _make_ollama_request(text: str, model: str) -> Optional[int]:
    """Выполняет запрос к Ollama с указанной моделью."""
    prompt = CLASSIFY_PROMPT.format(text=text)
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.0,
            "num_predict": 3,
            "top_p": 0.1,
        }
    }

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=OLLAMA_TIMEOUT
        )
        response.raise_for_status()
        
        result = response.json()
        answer = result.get("response", "").strip()
        
        for char in answer:
            if char in ["0", "1"]:
                return int(char)
        
        return None
    except (requests.exceptions.RequestException, json.JSONDecodeError, ValueError) as e:
        print(f"Ошибка запроса к модели {model}: {e}")
        return None

def classify_with_ollama(text: str) -> int:
    """Классифицирует текст с помощью Ollama."""
    if not test_ollama_connection():
        print("Ollama недоступна")
        return 0
    
    result = _make_ollama_request(text, OLLAMA_MODEL)
    if result is not None:
        return result
    
    print(f"Переключение на резервную модель {OLLAMA_FALLBACK_MODEL}")
    result = _make_ollama_request(text, OLLAMA_FALLBACK_MODEL)
    if result is not None:
        return result
    
    print(f"Переключение на бэкап модель {OLLAMA_BACKUP_MODEL}")
    result = _make_ollama_request(text, OLLAMA_BACKUP_MODEL)
    if result is not None:
        return result
    
    print("Все модели недоступны, письмо считается безопасным")
    return 0