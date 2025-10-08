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
            "temperature": 0.0,  # Максимально детерминированный ответ
            "num_predict": 3,    # Минимальный ответ - только цифра
            "top_p": 0.1,        # Ограничиваем вариативность
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
        
        # Извлекаем только первую цифру из ответа
        for char in answer:
            if char in ["0", "1"]:
                return int(char)
        
        return None
    except (requests.exceptions.RequestException, json.JSONDecodeError, ValueError) as e:
        print(f"Ошибка запроса к модели {model}: {e}")
        return None

def classify_with_ollama(text: str) -> int:
    """
    Классифицирует текст с помощью Ollama.
    Возвращает 1 (угроза) или 0 (безопасно).
    Использует резервную модель при ошибке основной.
    """
    if not test_ollama_connection():
        print("❌ Ollama недоступна")
        return 0  # В случае недоступности считаем письмо безопасным
    
    # Попытка с основной моделью (1.3 ГБ)
    result = _make_ollama_request(text, OLLAMA_MODEL)
    if result is not None:
        print(f"✅ Классификация выполнена моделью {OLLAMA_MODEL}: {result}")
        return result
    
    # Попытка с первой резервной моделью
    print(f"⚠️ Переключение на резервную модель {OLLAMA_FALLBACK_MODEL}")
    result = _make_ollama_request(text, OLLAMA_FALLBACK_MODEL)
    if result is not None:
        print(f"✅ Классификация выполнена резервной моделью {OLLAMA_FALLBACK_MODEL}: {result}")
        return result
    
    # Попытка с второй резервной моделью
    print(f"⚠️ Переключение на бэкап модель {OLLAMA_BACKUP_MODEL}")
    result = _make_ollama_request(text, OLLAMA_BACKUP_MODEL)
    if result is not None:
        print(f"✅ Классификация выполнена бэкап моделью {OLLAMA_BACKUP_MODEL}: {result}")
        return result
    
    print("❌ Все модели недоступны, письмо считается безопасным")
    return 0  # В случае ошибки считаем письмо безопасным
