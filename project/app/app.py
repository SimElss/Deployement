from fastapi import FastAPI, status, Depends
from app.routes.fr.routes import router as fr_router
from app.routes.fr.users import user_router as fr_user_router
from app.routes.en.routes import router as en_router
from app.routes.en.users import user_router as en_user_router
from fastapi.responses import RedirectResponse
from pydantic import ValidationError
from fastapi import Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.database import create_database, initialiser_db, delete_database, vider_db
from app.errors import ChangeMdpError
from dotenv import load_dotenv
from starlette.middleware.base import BaseHTTPMiddleware
from urllib.parse import urlencode


#Structure of the app
app = FastAPI()
#Routing files -> get pages and post infos
app.include_router(fr_router)
app.include_router(fr_user_router)
app.include_router(en_router)
app.include_router(en_user_router)
#Include css file(s) and images
app.mount("/static", StaticFiles(directory="static"), name="static")
#Locate templates (html pages) folder
templates = Jinja2Templates(directory="templates")

# Liste des langues disponibles
AVAILABLE_LANGUAGES = ["fr", "en"]
DEFAULT_LANGUAGE = "fr"

# ➤ Middleware pour la gestion de la langue utilisateur
class LanguageMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 1. Vérifier si une langue est définie dans les cookies
        lang = request.cookies.get("language")

        # 2. Vérifier si l'utilisateur a défini une langue dans l'URL
        lang_query = request.query_params.get("lang")
        if lang_query in AVAILABLE_LANGUAGES:
            lang = lang_query

        # 3. Utiliser la langue par défaut si aucune langue n'est définie
        if lang not in AVAILABLE_LANGUAGES:
            lang = DEFAULT_LANGUAGE

        # 4. Ajouter la langue à l'état de la requête
        request.state.lang = lang

        # 5. Appliquer la langue dans un cookie si nécessaire
        response = await call_next(request)
        response.set_cookie(key="language", value=lang)
        return response

app.add_middleware(LanguageMiddleware)

#Get any 404 error from app and catch it then redirect to tmp page -> tmp redirect then to error
#Why using tmp ? Impossible to import login_manager in app_file ? So we use tmp to see if user is connected or not 
#-> choose correct page to redirect after error page
@app.exception_handler(404)
def not_found(request: Request, exc):
    error = status.HTTP_404_NOT_FOUND
    description = f"Erreur {error} : page non trouvée"
    # Capture l'URL précédente
    previous_url = request.headers.get("referer", "/fr")
    # Encode l'URL précédente dans les paramètres
    query_params = urlencode({"description": description, "url": previous_url})
    return RedirectResponse(url=f"/fr/error?{query_params}", status_code=302)

@app.exception_handler(ValidationError)
def custom_validation_error_redirection(request: Request, exception: ValidationError):
    errors = exception.errors()
    error = status.HTTP_422_UNPROCESSABLE_ENTITY
    description = f"Erreur {error} : {errors[0]['msg']}"
    previous_url = request.headers.get("referer", "/fr/register")
    query_params = urlencode({"description": description, "url": previous_url})
    return RedirectResponse(url=f"/fr/error?{query_params}", status_code=302)

@app.exception_handler(ChangeMdpError)
def custom_change_mdp_error_redirection(request: Request, exception: ChangeMdpError):
    error = status.HTTP_422_UNPROCESSABLE_ENTITY
    description = f"Erreur {error} : {exception}"
    previous_url = request.headers.get("referer", "/fr/new_mdp")
    query_params = urlencode({"description": description, "url": previous_url})
    return RedirectResponse(url=f"/fr/error?{query_params}", status_code=302)

@app.on_event("startup")
def on_application_started():
    print("Good Morning World !")
    create_database()
    initialiser_db()

@app.on_event("shutdown")
def shutdown_event():
    delete_database()
    vider_db()


load_dotenv()