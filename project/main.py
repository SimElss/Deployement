import os
import uvicorn
from colorama import init
import signal
from app.app import handle_exit


if __name__ == "__main__":
    init()
    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)
    port = int(os.environ.get("PORT", 8000))  # 8000 est la valeur par défaut si PORT n'est pas défini
    uvicorn.run("app.app:app", host="0.0.0.0", port=port)
    