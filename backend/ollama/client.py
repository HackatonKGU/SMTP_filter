import requests
from config import OLLAMA_URL, OLLAMA_MODEL, CLASSIFY_PROMPT, OLLAMA_TIMEOUT

def classify_with_ollama(text: str) -> int:
    """
    Классифицирует текст с помощью Ollama.
    Возвращает 1 (угроза) или 0 (безопасно).
    """
    prompt = CLASSIFY_PROMPT.format(text=text)
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "temperature": 0.1,  # Детерминированный ответ
        "max_tokens": 5,     # Ограничиваем длину ответа
    }

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=OLLAMA_TIMEOUT
        )
        response.raise_for_status()
        answer = response.json()["response"].strip()
        return int(answer) if answer in ["0", "1"] else 0
    except requests.exceptions.RequestException as e:
        print(f"Ошибка Ollama: {e}")
        return 0  # В случае ошибки считаем письмо безопасным
