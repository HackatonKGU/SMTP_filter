# Порты
SMTP_PORT = 10025          # Ваш SMTP фильтр (прокси)
FLASK_PORT = 5000
API_PORT = 8000

# MailHog конфигурация
MAILHOG_SMTP_PORT = 1025   # MailHog SMTP сервер
MAILHOG_WEB_PORT = 8025    # MailHog веб-интерфейс
MAILHOG_HOST = "localhost"
MAILHOG_PATH = r"C:\Users\Awerson\source\repos\github_repos\SMTP_filter\mailhog\MailHog_windows_amd64.exe"

# Ollama
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "gemma3:4b"  # Лучшая модель по результатам тестов (90% точность)
OLLAMA_FALLBACK_MODEL = "mistral:7b-instruct-q4_0"  # Резервная модель
OLLAMA_BACKUP_MODEL = "llama3.2:1b"  # Легкая модель (только для экстренных случаев)
OLLAMA_TIMEOUT = 30  # Таймаут запроса к Ollama (секунды)

# База данных
DB_NAME = "blocked_emails.db"

# Промт для классификации угроз (оптимизирован для легких моделей)
CLASSIFY_PROMPT = """You are a security expert. Classify this text as threat (1) or safe (0).

Threats contain: explosives, bombs, violence, terrorism, killing, attacks
Safe texts: normal messages, work emails, friendly chat

Examples:
"I will bomb the building" → 1
"Meeting at 2pm" → 0
"Kill everyone" → 1
"Hello, how are you?" → 0

Text: "{text}"

Answer (only 0 or 1):"""
