from smtp.server import run_smtp_server
from config import SMTP_PORT

if __name__ == "__main__":
    run_smtp_server(SMTP_PORT)
