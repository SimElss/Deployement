import os
import uvicorn
from colorama import init
import signal


if __name__ == "__main__":
    init()
    port = int(os.environ.get("PORT", 8000))  # 8000 est la valeur par défaut si PORT n'est pas défini
    uvicorn.run("app.app:app", host="0.0.0.0", port=port)
    