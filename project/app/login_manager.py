from fastapi_login import LoginManager # type: ignore
from datetime import timedelta

from app.services.users import get_user_by_id # type: ignore

#Chose secret
SECRET = "SECRET"
#Set cookie and time_expiry -> 1 hour
login_manager = LoginManager(SECRET, '/login', use_cookie=True, default_expiry=timedelta(hours = 1))
login_manager.cookie_name = "auth_cookie"

#Very important ! We can call it later using Depends() to see if a user and which one is currently connected or not
@login_manager.user_loader()
def query_user(user_id: str):
    return get_user_by_id(user_id)