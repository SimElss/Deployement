from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from ...services.users import add_user, get_all_users, get_user_by_id, set_user_group, set_user_whitelist, get_user_by_email, change_user_password
from fastapi import status, Depends, Form
from ...login_manager import login_manager
from fastapi.responses import RedirectResponse
from ...schemas.users import UserSchema
from typing import Annotated
from uuid import uuid4
import hashlib

# Define APIRouter instance for user routes
user_router = APIRouter()

# Setup Jinja2Templates for HTML rendering
templatesfr = Jinja2Templates(directory="templates/fr")

# Route for user login page
@user_router.get("/fr/login")
def login(request: Request, message: str = "None", user: UserSchema = Depends(login_manager.optional)):
    """
    Displays the login page or redirects to the responsible homepage if the user is already logged in.
    """
    if user is None: 
        return templatesfr.TemplateResponse(
            "login.html", 
            context={'request': request, 'message': message, 'group': None }
        )
    else:
        return RedirectResponse(url="/fr/accueilResponsable", status_code=302)

# Route for handling user login
@user_router.post("/fr/login")
def login_route(
        email: Annotated[str, Form()],
        password: Annotated[str, Form()],
):
    """
    Handles user login by verifying credentials and creating an access token.
    """
    user = get_user_by_email(email)
    encoded_password = password.encode()
    hashed_password = hashlib.sha3_256(encoded_password).hexdigest()
    
    # Vérifier si l'utilisateur existe et si le mot de passe est correct
    if user is None or user.password != hashed_password:
        error_message = "Incorrect username or password."
        return templatesfr.TemplateResponse(
            "login.html",
            context={'request': {}, 'message': error_message, 'group': None}
        )
    
    # Vérifier si l'utilisateur est bloqué
    if not user.whitelist:
        error_message = "User blocked."
        return templatesfr.TemplateResponse(
            "login.html",
            context={'request': {}, 'message': error_message, 'group': None}
        )
        
    # Créer un token d'accès et rediriger vers la page d'accueil
    access_token = login_manager.create_access_token(data={'sub': user.id})
    response = RedirectResponse(url="/fr/accueilResponsable", status_code=302)
    response.set_cookie(key=login_manager.cookie_name, value=access_token, httponly=True)
    return response

# Route for user logout
@user_router.post('/fr/logout')
def logout(request: Request):
    """
    Logs out the user by deleting the access token cookie and displaying the login page.
    """
    response = templatesfr.TemplateResponse(
        "login.html", 
        context={'request': request, 'message': "You have been logged out!", 'group': None}
    )
    response.delete_cookie(key=login_manager.cookie_name, httponly=True)
    return response

# Route for user registration page
@user_router.get('/fr/register')
def register(request: Request):
    """
    Displays the registration page for new users.
    """
    return templatesfr.TemplateResponse(
        "register.html", 
        context={'request': request, 'group': None}
    )

# Route for handling user registration
@user_router.post('/fr/register')
def register_route(request: Request, username: Annotated[str, Form()], name: Annotated[str, Form()], surname: Annotated[str, Form()], email: Annotated[str, Form()], password: Annotated[str, Form()], password_confirm: Annotated[str, Form()],
):
    """
    Handles user registration by validating input and adding the user to the database.
    """
    user = get_user_by_email(email)
    if user is not None:
        error = status.HTTP_409_CONFLICT
        description = f"Error {error}: Email already in use."
        return RedirectResponse(url=f"fr/error/{description}/fr/register", status_code=302)
    
    if password != password_confirm:
        error = status.HTTP_400_BAD_REQUEST
        description = f"Error {error}: Passwords do not match."
        return RedirectResponse(url=f"fr/error/{description}/fr/register", status_code=302)
    
    new_user = {
        "id": str(uuid4()),
        "username": username,
        "name": name,
        "surname": surname,
        "password": password,
        "email": email,
        "group": "candidat",
        "whitelist": True,
        "notification": ""  # Default value for notification
    }
    new_user = UserSchema.model_validate(new_user)
    add_user(new_user)
    success_message = f"User {username} successfully added!"
    return templatesfr.TemplateResponse(
        "login.html",
        context={'request': request, 'message': success_message, 'current_user': None, 'group': None}
    )

# Route for password reset page
@user_router.get('/fr/new_mdp')
def new_mdp(request: Request, user: UserSchema = Depends(login_manager.optional)):
    """
    Displays the password reset page.
    """
    required = user is not None
    return templatesfr.TemplateResponse(
        "new_mdp.html", 
        context={'request': request, 'current_user': user, 'required': required, 'group': None}
    )

@user_router.post('/fr/new_mdp')
def new_mdp_route(
    request: Request,
    old_pwd: Annotated[str, Form()],
    new_pwd: Annotated[str, Form()],
    new_pwd_confirm: Annotated[str, Form()],
    user: UserSchema = Depends(login_manager.optional),
    email: Annotated[str, Form()] = None,
):
    """
    Handles password reset by verifying the old password and updating it with the new one.
    """
    if user is None:
        target_user = get_user_by_email(email)
        if target_user is None:
            error = status.HTTP_404_NOT_FOUND
            description = f"Error {error}: User not found."
            return RedirectResponse(url=f"/error/{description}/fr/new_mdp", status_code=302)
    else:
        target_user = user

    encoded_password = old_pwd.encode()
    old_hashed_password = hashlib.sha3_256(encoded_password).hexdigest()
    if target_user.password != old_hashed_password:
        error = status.HTTP_400_BAD_REQUEST
        description = f"Error {error}: Old password is incorrect."
        return RedirectResponse(url=f"/error/{description}/fr/new_mdp", status_code=302)
    
    if new_pwd != new_pwd_confirm:
        error = status.HTTP_400_BAD_REQUEST
        description = f"Error {error}: Passwords do not match."
        return RedirectResponse(url=f"/error/{description}/fr/new_mdp", status_code=302)

    # Change the user's password
    change_user_password(target_user.id, new_pwd)
    success_message = "Password successfully updated! Please log in again."

    # Redirect to the login page with a success message
    return templatesfr.TemplateResponse(
        "login.html",
        context={'request': request, 'message': success_message, 'current_user': None, 'group': None}
    )
