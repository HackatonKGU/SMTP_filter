import asyncio
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from smtp.server import run_smtp_server
from config import SMTP_PORT, API_PORT
from health_check import check_db_connection

app = FastAPI()

app.mount("/interface", StaticFiles(directory="interface", html=True), name="interface")


@app.get("/health")
def health():
    return {"database": check_db_connection()}


async def main():
    loop = asyncio.get_running_loop()
    smtp_server_task = loop.run_in_executor(None, run_smtp_server, SMTP_PORT)

    config = uvicorn.Config(app, host="0.0.0.0", port=API_PORT, log_level="info")
    api_server = uvicorn.Server(config)

    await asyncio.gather(smtp_server_task, api_server.serve())

if __name__ == "__main__":
    asyncio.run(main())
