import uvicorn
from colorama import init
import signal
from app.app import handle_exit


if __name__ == "__main__":
    init()
    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)
    #Get app variable from app file in app folder (app.app)
    uvicorn.run("app.app:app", host="127.0.0.1", port=8000)