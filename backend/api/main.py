import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from typing import Optional

from core.config import API_PORT
from api.health_check import check_db_connection
from core.database.repo import (
    get_blocked_emails,
    get_blocked_email_by_id,
    get_blocked_emails_count,
    delete_blocked_email,
    clear_all_blocked_emails
)

app = FastAPI()

# Подключаем статические файлы для интерфейса
app.mount("/interface", StaticFiles(directory="web/interface", html=True), name="interface")

@app.get("/health")
def health():
    return {"database": check_db_connection()}

# --- API для работы с заблокированными письмами ---

@app.get("/api/blocked-emails")
def get_blocked_emails_api(
    limit: int = Query(50, ge=1, le=200),
    page: int = Query(1, ge=1)
):
    offset = (page - 1) * limit
    emails = get_blocked_emails(limit=limit, offset=offset)
    total_count = get_blocked_emails_count()
    return {
        "emails": emails,
        "total": total_count,
        "page": page,
        "limit": limit,
        "total_pages": (total_count + limit - 1) // limit if total_count > 0 else 1
    }

@app.get("/api/blocked-emails/{email_id}")
def get_blocked_email_api(email_id: int):
    email = get_blocked_email_by_id(email_id)
    if not email:
        raise HTTPException(status_code=404, detail="Письмо не найдено")
    return email

@app.delete("/api/blocked-emails/{email_id}")
def delete_blocked_email_api(email_id: int):
    success = delete_blocked_email(email_id)
    if not success:
        raise HTTPException(status_code=404, detail="Письмо не найдено для удаления")
    return {"message": "Письмо успешно удалено"}

@app.delete("/api/blocked-emails")
def clear_all_blocked_emails_api():
    clear_all_blocked_emails()
    return {"message": "Все заблокированные письма были удалены"}

@app.get("/api/stats")
def get_stats_api():
    return {
        "blocked_emails_count": get_blocked_emails_count(),
        "database_status": check_db_connection(),
    }