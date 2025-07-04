from datetime import datetime
from multiprocessing.resource_tracker import getfd
from pathlib import Path
from typing import Annotated, Optional
from uuid import uuid4
from fastapi import APIRouter, HTTPException, status, Request, Depends, Query, Form, File, UploadFile
from app.database import Session
from app.services.users import update_user_profile
from ...login_manager import login_manager
from ...schemas.users import UserSchema
from fastapi.responses import JSONResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from app.models.models import DetailsDossierCandidats, DossierCandidats, Users
from app.services.folder import add_details_dossier_candidat, add_dossier_candidat, delete_candidat, get_dossier_by_id, get_details_dossier_by_id, get_dossiers_by_candidat, update_dossier, update_dossier_details, search_dossiers
from sqlalchemy.orm import joinedload
import pandas as pd
import io

# Create APIRouter instance for routes
router = APIRouter()

# Setup Jinja2templatesfr for HTML rendering
templatesfr = Jinja2Templates(directory="templates/fr")
templatesen = Jinja2Templates(directory="templates/en")

# Route for redirecting to the French version of the site
@router.get("/")
def home():
    """
    Redirects to the French version of the site.
    """
    return RedirectResponse(url="/en", status_code=302)

# Temporary route to handle user session management
@router.get("/en/tmp")
def tmp(request: Request, user: UserSchema = Depends(login_manager.optional)):
    """
    Redirects connected users to the responsible homepage
    and non-connected users to the login page.
    """
    if user is None:
        return RedirectResponse(url="/en/login", status_code=302)
    else:
        return RedirectResponse(url="/en/accueilResponsable", status_code=302)

# Route for redirecting to the French login page
@router.get("/en")
def homeen():
    """
    Redirects to the French login page.
    """
    return RedirectResponse(url="/en/login", status_code=302)

# Route for switching to the french version of the site
@router.get("/en/switch_to_fr")
def switch_to_french():
    """
    Redirects the user to the English version of the site.
    """
    return RedirectResponse(url="/fr", status_code=302)

# Route to display an error message
@router.get("/en/error/{description}/{url}")
def error(request: Request, description: str, url: str):
    """
    Displays an error page with a description and a redirection link.
    """
    return templatesen.TemplateResponse(
        "error.html",
        context={'request': request, 'description': description, 'url': url}
    )

# Route for the main page for responsible users
@router.get("/en/accueilResponsable")
def list_mainpage(request: Request, user: UserSchema = Depends(login_manager.optional)):
    """
    Displays the main page for responsible users.
    Redirects candidates to their homepage.
    """
    if user and user.group == 'candidat':
        return RedirectResponse(url="/en/accueil", status_code=302)
    
    session = Session()
    candidats = session.query(DossierCandidats).all()  # Retrieve all candidate files
    has_missing_details = any(candidat.details is None for candidat in candidats)
    session.close()

    return templatesen.TemplateResponse(
        "mainpage.html",
        context={'request': request, 'current_user': user, 'group': user.group, 'candidats': candidats , 'has_missing_details': has_missing_details}
    )

# Route for the main page for candidates
@router.get("/en/accueil")
def mainpage_candidat(request: Request, user: UserSchema = Depends(login_manager.optional)):
    """
    Displays the main page for connected candidates.
    Redirects non-connected users to the login page.
    """
    if user is None:
        return RedirectResponse(url="/en/login", status_code=302)
    
    session = Session()

    # Retrieve files linked to the user
    dossiers = session.query(DossierCandidats).filter(DossierCandidats.mail == user.email).all()
    has_missing_details = any(candidat.details is None for candidat in dossiers)

    session.close()

    return templatesen.TemplateResponse(
        "mainpage_candidat.html",
        context={
            'request': request,
            'current_user': user,
            'group': user.group,
            'dossiers': dossiers,
            'has_missing_details': has_missing_details,
        }
    )

# Route for listing all candidate files
@router.get("/en/dossier")
def list_mainpage(request: Request, user: UserSchema = Depends(login_manager.optional), page: int = Query(1, ge=1), per_page: int = Query(10, ge=1)):
    """
    Displays a paginated list of all candidate files.
    Redirects candidates to their specific dossier page.
    """
    if user.group == 'candidat':
        return RedirectResponse(url="/en/dossiercandidat", status_code=302)
    
    session = Session()
    total_candidats = session.query(DossierCandidats).count()
    candidats = session.query(DossierCandidats).options(joinedload(DossierCandidats.details)).offset((page - 1) * per_page).limit(per_page).all()
    has_missing_details = any(candidat.details is None for candidat in candidats)
    session.close()

    return templatesen.TemplateResponse(
        "dossier.html",
        context={
            'request': request,
            'current_user': user,
            'group': user.group,
            'candidats': candidats,
            'page': page,
            'per_page': per_page,
            'total_candidats': total_candidats,
            'has_missing_details': has_missing_details
        }
    )

# Route for listing candidate-specific files
@router.get("/en/dossiercandidat")
def list_dossiers_candidat(request: Request, user: UserSchema = Depends(login_manager), page: int = Query(1, ge=1), per_page: int = Query(5, ge=1)):
    """
    Displays a paginated list of files specific to the connected candidate.
    Redirects non-connected users to the login page.
    """
    if user is None:
        return RedirectResponse(url="/en/login", status_code=302)
    
    session = Session()
    total_dossiers = session.query(DossierCandidats).filter(DossierCandidats.user_id == user.id).count()
    dossiers = session.query(DossierCandidats).options(joinedload(DossierCandidats.details)).filter(DossierCandidats.mail == user.email).offset((page - 1) * per_page).limit(per_page).all()
    has_missing_details = any(dossier.details is None for dossier in dossiers)
    session.close()
    
    return templatesen.TemplateResponse(
        "dossiercandidat.html",
        context={
            'request': request,
            'current_user': user,
            'dossiers': dossiers,
            'page': page,
            'per_page': per_page,
            'total_candidats': total_dossiers,
            'has_missing_details': has_missing_details,
            'notifications': user.notification
        }
    )


@router.get("/en/dossier")
def list_mainpage(request: Request, user: UserSchema = Depends(login_manager.optional), page: int = Query(1, ge=1), per_page: int = Query(10, ge=1)):
    """
    Displays a paginated list of all candidate files.
    Redirects candidates to their specific dossier page.
    """
    if user.group == 'candidat':
        return RedirectResponse(url="/en/dossiercandidat", status_code=302)
    
    session = Session()
    total_candidats = session.query(DossierCandidats).count()
    candidats = session.query(DossierCandidats).options(joinedload(DossierCandidats.details)).offset((page - 1) * per_page).limit(per_page).all()
    has_missing_details = any(candidat.details is None for candidat in candidats)
    session.close()

    return templatesen.TemplateResponse(
        "dossier.html",
        context={
            'request': request,
            'current_user': user,
            'group': user.group,
            'candidats': candidats,
            'page': page,
            'per_page': per_page,
            'total_candidats': total_candidats,
            'has_missing_details': has_missing_details
        }
    )

@router.get("/en/dossiercandidat")
def list_dossiers_candidat(request: Request, user: UserSchema = Depends(login_manager), page: int = Query(1, ge=1), per_page: int = Query(5, ge=1)):
    """
    Displays a paginated list of files specific to the connected candidate.
    Redirects non-connected users to the login page.
    """
    if user is None:
        return RedirectResponse(url="/en/login", status_code=302)
    
    session = Session()
    total_dossiers = session.query(DossierCandidats).filter(DossierCandidats.user_id == user.id).count()
    dossiers = session.query(DossierCandidats).options(joinedload(DossierCandidats.details)).filter(DossierCandidats.user_id == user.id).offset((page - 1) * per_page).limit(per_page).all()
    has_missing_details = any(dossier.details is None for dossier in dossiers)
    session.close()
    
    return templatesen.TemplateResponse(
        "dossiercandidat.html",
        context={
            'request': request,
            'current_user': user,
            'dossiers': dossiers,
            'page': page,
            'per_page': per_page,
            'total_candidats': total_dossiers,
            'has_missing_details': has_missing_details,
            'notifications': user.notification
        }
    )

@router.get("/en/dossier/{id}")
def show_dossier_details(request: Request, id: str, user: UserSchema = Depends(login_manager.optional)):
    """
    Displays the details of a specific dossier.
    Redirects to the add details page if no details are associated with the dossier.
    """


    dossier, has_missing_details = get_dossier_by_id(id)
    details = get_details_dossier_by_id(id)

    
    if not dossier:
        return {"error": "Dossier not found"}
    
    if not details:
        return RedirectResponse(url=f"/en/details/add/{id}", status_code=302)
    
    now = datetime.now()
    timeline_dates = [
        {"label": "Closing date", "date": details.date_cloture},
        {"label": "Reception date", "date": details.date_reception},
        {"label": "Date sent to the committee", "date": details.date_transmission_commission},
        {"label": "Committee meeting date", "date": details.date_reunion_commission},
        {"label": "Date when the candidate will be interviewed", "date": details.date_entendu},
        {"label": "Date submitted to faculty authorities", "date": details.date_soumission_autorites},
        {"label": "Date sent to authorities", "date": details.date_transmission_autorites},
        {"label": "Expected start date", "date": details.date_entree_fonction},
        {"label": "File deletion date", "date": details.date_suppression_dossier},
    ]

    # Trier les dates par ordre chronologique
    timeline_dates = sorted(
        [d for d in timeline_dates if d["date"]],  # Exclure les dates nulles
        key=lambda x: x["date"]
    )
    
    return templatesen.TemplateResponse(
        "dossier_detail.html",
        context={
            'request': request,
            'current_user': user,
            'group': user.group,
            'dossier': dossier,
            'details': details,
            'has_missing_details': has_missing_details,
            'now': now,
            'timeline_dates': timeline_dates,
        }
    )

@router.get("/en/profile")
def get_profile(request: Request, user: UserSchema = Depends(login_manager.optional)):
    """
    Displays the profile page of the connected user.
    Redirects non-connected users to the login page.
    """
    if user is None:
        return RedirectResponse(url="/en/login", status_code=302)
    return templatesen.TemplateResponse(
        "profile.html",
        context={'request': request, 'current_user': user, 'group': user.group}
    )

@router.post("/en/profile")
def update_profile(request: Request, name: str = Form(...), surname: str = Form(...), username: str = Form(...), user: UserSchema = Depends(login_manager.optional)):
    """
    Updates the profile information of the connected user.
    Redirects non-connected users to the login page.
    """
    if user is None:
        return RedirectResponse(url="/en/login", status_code=302)
    
    success = update_user_profile(user.id, name, surname, username)
    if success:
        return RedirectResponse(url="/en/profile", status_code=302)
    else:
        raise HTTPException(status_code=404, detail="User not found")

@router.get("/en/modify_detail/{id}")
def get_modify_detail_form(request: Request, id: str, user: UserSchema = Depends(login_manager.optional)):
    """
    Displays a form to modify the details of a specific dossier.
    """
    dossier = get_dossier_by_id(id)
    details = get_details_dossier_by_id(id)

    return templatesen.TemplateResponse(
        "modify_detail.html",
        context={"request": request, "dossier": dossier[0],"details": details, "current_user": user}
    )

@router.post("/en/modify_detail/{dossier_id}")
def post_modify_detail(
    dossier_id: str,
    mail: str = Form(...),
    phonenumber: str = Form(...),
    date_cloture: str = Form(...),
    date_reception: str = Form(...),
    dossier_complet: str = Form(...),
    date_transmission_commission: str = Form(None),
    date_reunion_commission: str = Form(None),
    candidature_non_retenue: str = Form(...),
    confirmation_information: str = Form(...),
    date_entendu: str = Form(None),
    position_classement: int = Form(None),
    date_soumission_autorites: str = Form(None),
    date_transmission_autorites: str = Form(None),
    date_entree_fonction: str = Form(None),
    date_suppression_dossier: str = Form(None),
    user: UserSchema = Depends(login_manager.optional)
):
    """
    Updates the details of a specific dossier.
    Redirects to the login page if the user is not connected.
    """
    if user is None:
        return RedirectResponse(url="/login", status_code=302)
    
    success = update_dossier_details(
        dossier_id=dossier_id,
        mail=mail,
        phonenumber=phonenumber,
        date_cloture=date_cloture,
        date_reception=date_reception,
        dossier_complet=dossier_complet,
        date_transmission_commission=date_transmission_commission,
        date_reunion_commission=date_reunion_commission,
        candidature_non_retenue=candidature_non_retenue,
        confirmation_information=confirmation_information,
        date_entendu=date_entendu,
        position_classement=position_classement,
        date_soumission_autorites=date_soumission_autorites,
        date_transmission_autorites=date_transmission_autorites,
        date_entree_fonction=date_entree_fonction,
        date_suppression_dossier=date_suppression_dossier
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Dossier or details not found")
    
    return RedirectResponse(url=f"/en/dossier/{dossier_id}", status_code=302)

@router.get("/en/edit_dossier/{dossier_id}")
def get_edit_dossier_form(request: Request, dossier_id: str, user: UserSchema = Depends(login_manager.optional)):
    """
    Displays a form to edit the basic information of a dossier.
    Redirects to the login page if the user is not connected.
    """
    if user is None:
        return RedirectResponse(url="/en/login", status_code=302)

    dossier = get_dossier_by_id(dossier_id)

    return templatesen.TemplateResponse(
        "modify_dossier.html",
        context={"request": request, "dossier": dossier[0], "current_user": user}
    )

@router.post("/en/edit/{dossier_id}")
def post_edit_dossier(
    dossier_id: str,
    name: str = Form(...),
    mail: str = Form(...),
    phonenumber: str = Form(...),
    postereference: str = Form(...),
    user: UserSchema = Depends(login_manager.optional)
):
    """
    Updates the basic information of a dossier.
    Redirects to the login page if the user is not connected.
    """
    if user is None:
        return RedirectResponse(url="/en/login", status_code=302)
    
    success = update_dossier(
        dossier_id=dossier_id,
        name=name,
        mail=mail,
        phonenumber=phonenumber,
        postereference=postereference
    )

    return RedirectResponse(url=f"/en/dossier/{dossier_id}", status_code=302)

@router.post("/en/dossier/search")
def search_dossiers_route(
    request: Request,
    keyword: str = Form(...),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1),
    user: UserSchema = Depends(login_manager.optional)
):
    """
    Searches for dossiers based on a keyword.
    Displays the search results in a paginated format.
    """
    dossiers, has_missing_details = search_dossiers(keyword, page, per_page)
    
    return templatesen.TemplateResponse(
        "dossier.html",
        context={
            'request': request,
            'current_user': user,
            'group': user.group,
            'candidats': dossiers,
            'page': page,
            'per_page': per_page,
            'total_candidats': len(dossiers),
            'keyword': keyword,
            'has_missing_details': has_missing_details
        }
    )

@router.post("/en/dossier/searchcandidat")
def search_dossiers_route_candidat(
    request: Request,
    keyword: str = Form(...),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1),
    user: UserSchema = Depends(login_manager.optional)
):
    """
    Searches for dossiers based on a keyword.
    Displays the search results in a paginated format.
    """

    dossiers, has_missing_details = search_dossiers(keyword, page, per_page)
    
    return templatesen.TemplateResponse(
        "dossiercandidat.html",
        context={
            'request': request,
            'current_user': user,
            'group': user.group,
            'dossiers': dossiers,
            'keyword': keyword,
            'has_missing_details': has_missing_details,
            'notifications': user.notification
        }
    )

@router.post("/en/dossier/delete/search")
def search_dossiers_route(
    request: Request,
    keyword: str = Form(...),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1),
    user: UserSchema = Depends(login_manager.optional)
):
    """
    Searches for dossiers to delete based on a keyword.
    Displays the search results in a paginated format.
    """
    dossiers = search_dossiers(keyword, page, per_page)
    
    return templatesen.TemplateResponse(
        "supp_dossier.html",
        context={
            'request': request,
            'current_user': user,
            'group': user.group,
            'candidats': dossiers,
            'page': page,
            'per_page': per_page,
            'total_candidats': len(dossiers),
            'keyword': keyword
        }
    )

@router.get("/en/notif/dossier")
def get_notif_dossier_form(request: Request, user: UserSchema = Depends(login_manager.optional), page: int = Query(1, ge=1), per_page: int = Query(10, ge=1)):
    """
    Displays a list of dossiers for sending notifications.
    Redirects candidates to their specific dossier page.
    """
    if user.group == 'candidat':
        return RedirectResponse(url="/en/dossiercandidat", status_code=302)
    
    session = Session()
    total_candidats = session.query(DossierCandidats).count()
    candidats = session.query(DossierCandidats).offset((page - 1) * per_page).limit(per_page).all()
    session.close()

    return templatesen.TemplateResponse(
        "notif_user.html",
        context={'request': request, 'current_user': user, 'group': user.group, 'candidats': candidats, 'page': page, 'per_page': per_page, 'total_candidats': total_candidats} 
    )

@router.get("/en/notif/{dossier_id}/notification")
def get_notification_form(
    dossier_id: str,
    request: Request,
    user: UserSchema = Depends(login_manager.optional)
):
    """
    Displays a form to send a notification to the user associated with a dossier.
    Redirects to the login page if the user is not connected.
    """
    if user is None:
        return RedirectResponse(url="/en/login", status_code=302)

    with Session() as session:
        dossier = session.query(DossierCandidats).filter(DossierCandidats.id == dossier_id).first()
        if not dossier:
            raise HTTPException(status_code=404, detail="Dossier not found")

        associated_user = session.query(Users).filter(Users.id == dossier.user_id).first()
        if not associated_user:
            raise HTTPException(status_code=404, detail="Associated user not found")

    return templatesen.TemplateResponse(
        "send_notif_user.html",
        context={
            "request": request,
            "current_user": user,
            "dossier": dossier,
            "associated_user": associated_user
        }
    )

@router.get("/en/dossier/export/excel")
def export_dossiers_to_excel(user: UserSchema = Depends(login_manager.optional)):
    """
    Generates an Excel file containing all dossiers and downloads it.
    Redirects to the login page if the user is not connected.
    """
    if user is None:
        return RedirectResponse(url="/en/login", status_code=302)

    with Session() as session:
        dossiers = session.query(DossierCandidats).all()

    # Convert dossiers to a pandas DataFrame
    data = [
        {
            "Name": dossier.name,
            "Email": dossier.mail,
            "Phone": dossier.phonenumber,
            "Post Reference": dossier.postereference,
            "Referring Professor": dossier.profref,
        }
        for dossier in dossiers
    ]
    df = pd.DataFrame(data)

    # Create an Excel file in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Dossiers")

        # Customize the Excel file
        workbook = writer.book
        worksheet = writer.sheets["Dossiers"]

        # Add a title above the columns
        worksheet.merge_range('A1:E1', 'List of Dossiers', workbook.add_format({
            'bold': True,
            'font_size': 14,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#D9EAD3'
        }))

        # Apply styles to the columns
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#D7E4BC',
            'border': 1
        })
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(1, col_num, value, header_format)

        # Adjust column widths
        worksheet.set_column('A:A', 10)  # ID
        worksheet.set_column('B:B', 20)  # Name
        worksheet.set_column('C:C', 30)  # Email
        worksheet.set_column('D:D', 15)  # Phone
        worksheet.set_column('E:E', 25)  # Post Reference
        worksheet.set_column('F:F', 25)  # Referring Professor

    output.seek(0)

    # Return the Excel file as a response
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=Dossiers_List.xlsx"}
    )

@router.post("/en/dossier/{dossier_id}/notification")
def send_notification(
    dossier_id: str,
    request: Request,
    message: str = Form(...),
    user: UserSchema = Depends(login_manager.optional)
):
    """
    Sends a notification to the user associated with a dossier.
    Redirects to the login page if the user is not connected.
    """
    if user is None:
        return RedirectResponse(url="/en/login", status_code=302)

    with Session() as session:
        dossier = session.query(DossierCandidats).filter(DossierCandidats.id == dossier_id).first()
        if not dossier:
            raise HTTPException(status_code=404, detail="Dossier not found")

        associated_user = session.query(Users).filter(Users.id == dossier.user_id).first()
        if not associated_user:
            raise HTTPException(status_code=404, detail="Associated user not found")

        # Add the notification
        associated_user.notification = message
        session.commit()

    return RedirectResponse(url="/en/notif/dossier", status_code=302)

@router.get("/en/dossier/supp/candidat")
def get_add_dossier_form(request: Request, user: UserSchema = Depends(login_manager.optional), page: int = Query(1, ge=1), per_page: int = Query(10, ge=1)):
    """
    Displays a list of dossiers for deletion.
    Redirects candidates to their specific dossier page.
    """
    if user.group == 'candidat':
        return RedirectResponse(url="/en/dossiercandidat", status_code=302)
    
    session = Session()
    total_candidats = session.query(DossierCandidats).count()
    candidats = session.query(DossierCandidats).offset((page - 1) * per_page).limit(per_page).all()
    session.close()

    return templatesen.TemplateResponse(
        "supp_dossier.html",
        context={'request': request, 'current_user': user, 'group': user.group, 'candidats': candidats, 'page': page, 'per_page': per_page, 'total_candidats': total_candidats} 
    )

@router.get("/en/dossier/candidat/delete/{candidat_id}")
def delete_candidat_route(candidat_id: str, request: Request, user: UserSchema = Depends(login_manager.optional)):
    """
    Deletes a specific candidate dossier.
    Redirects to the login page if the user is not connected.
    """
    if user is None:
        return RedirectResponse(url="/en/login", status_code=302)
    
    success = delete_candidat(candidat_id)
    if success:
        return RedirectResponse(url="/en/dossier", status_code=302)
    else:
        raise HTTPException(status_code=500, detail="Failed to delete candidate")

@router.get("/en/dossier/new/add")
def get_add_dossier_form(request: Request, user: UserSchema = Depends(login_manager.optional)):
    """
    Displays a form to add a new dossier.
    Redirects to the login page if the user is not connected.
    """
    if user is None:
        return RedirectResponse(url="/en/login", status_code=302)
    
    return templatesen.TemplateResponse(
        "add_dossier.html",
        context={"request": request, "current_user": user}
    )

@router.post("/en/dossier/new/add")
async def post_add_dossier(
    request: Request,
    username: str = Form(...),
    name: str = Form(...),
    mail: str = Form(...),
    postereference: str = Form(...),
    profref: str = Form(...),
    phonenumber: str = Form(...),
    image: UploadFile = File(None),
    user: UserSchema = Depends(login_manager.optional)
):
    """
    Adds a new dossier to the database.
    Redirects to the login page if the user is not connected.
    """
    if user is None:
        return RedirectResponse(url="/en/login", status_code=302)
    if user and user.group == 'candidat':
        return RedirectResponse(url="/en/accueil", status_code=302)
    
    default_image_path = "../static/images/incognito.png"

    # Vérifier si un fichier a été uploadé
    if image and image.filename != "":
        valid_extensions = ["jpg", "jpeg", "png"]
        file_extension = image.filename.split(".")[-1].lower()
        if file_extension not in valid_extensions:
            raise HTTPException(status_code=400, detail="Invalid file format. Only .jpg, .jpeg, and .png are allowed.")

        # Construire le chemin de sauvegarde
        static_dir = Path("./static/images")
        static_dir.mkdir(parents=True, exist_ok=True)  # Créer le dossier s'il n'existe pas
        file_name = f"{username}_{name}.{file_extension}"
        file_path = static_dir / file_name

        # Sauvegarder le fichier
        with open(file_path, "wb") as f:
            f.write(await image.read())

        relative_path = f"../static/images/{file_name}"
    else:
        relative_path = default_image_path
    
    new_dossier = add_dossier_candidat(
        username=username,
        name=name,
        mail=mail,
        postereference=postereference,
        profref=profref,
        phonenumber=phonenumber,
        image=relative_path if image else None,
        user_id=user.id
    )
    return RedirectResponse(url=f"/en/details/add/{new_dossier.id}", status_code=302)

@router.get("/en/details/add/{dossier_id}")
def get_add_details_form(request: Request, dossier_id: str, user: UserSchema = Depends(login_manager.optional)):
    """
    Displays a form to add details to a specific dossier.
    Redirects to the login page if the user is not connected.
    """
    if user is None:
        return RedirectResponse(url="/en/login", status_code=302)
    
    dossier = get_dossier_by_id(dossier_id)
    if not dossier:
        raise HTTPException(status_code=404, detail="Dossier not found")
    
    return templatesen.TemplateResponse(
        "add_details.html",
        context={"request": request, "dossier": dossier[0], "current_user": user}
    )

@router.post("/en/details/add/{dossier_id}")
def post_add_details(
    request: Request,
    dossier_id: str,
    date_cloture: str = Form(None),
    date_reception: str = Form(None),
    dossier_complet: bool = Form(False),
    date_transmission_commission: str = Form(None),
    date_reunion_commission: str = Form(None),
    candidature_non_retenue: bool = Form(False),
    confirmation_information: bool = Form(False),
    date_entendu: str = Form(None),
    position_classement: int = Form(None),
    date_soumission_autorites: str = Form(None),
    date_transmission_autorites: str = Form(None),
    date_entree_fonction: str = Form(None),
    date_suppression_dossier: str = Form(None),
    user: UserSchema = Depends(login_manager.optional)
):
    """
    Adds details to a specific dossier.
    Redirects to the login page if the user is not connected.
    """
    if user is None:
        return RedirectResponse(url="/en/login", status_code=302)
    
    success = add_details_dossier_candidat(
        dossier_id=dossier_id,
        date_cloture=date_cloture,
        date_reception=date_reception,
        dossier_complet=dossier_complet,
        date_transmission_commission=date_transmission_commission,
        date_reunion_commission=date_reunion_commission,
        candidature_non_retenue=candidature_non_retenue,
        confirmation_information=confirmation_information,
        date_entendu=date_entendu,
        position_classement=position_classement,
        date_soumission_autorites=date_soumission_autorites,
        date_transmission_autorites=date_transmission_autorites,
        date_entree_fonction=date_entree_fonction,
        date_suppression_dossier=date_suppression_dossier
    )
    if not success:
        raise HTTPException(status_code=400, detail="Failed to add details")
    
    return RedirectResponse(url=f"/en/dossier/{dossier_id}", status_code=302)

@router.get("/en/admin/users")
def get_users_with_groups(request: Request, user: UserSchema = Depends(login_manager.optional)):
    """
    Affiche une liste des utilisateurs avec leurs groupes actuels.
    Permet de modifier le groupe de chaque utilisateur individuellement.
    """
    if user is None:
        return RedirectResponse(url="/en/login", status_code=302)
    if user.group != 'admin':  # Vérifie si l'utilisateur est un administrateur
        raise HTTPException(status_code=403, detail="Access forbidden")

    with Session() as session:
        users = session.query(Users).all()

    return templatesen.TemplateResponse(
        "change_group.html",
        context={"request": request, "current_user": user, "users": users}
    )

@router.post("/en/admin/users/update")
def update_user_group(
    request: Request,
    user_id: str = Form(...),
    new_group: str = Form(...),
    user: UserSchema = Depends(login_manager.optional)
):
    """
    Met à jour le groupe d'un utilisateur spécifique.
    """
    if user is None:
        return RedirectResponse(url="/en/login", status_code=302)
    if user.group != 'admin':  # Vérifie si l'utilisateur est un administrateur
        raise HTTPException(status_code=403, detail="Access forbidden")

    with Session() as session:
        user_to_update = session.query(Users).filter(Users.id == user_id).first()
        if not user_to_update:
            raise HTTPException(status_code=404, detail="User not found")
        user_to_update.group = new_group
        session.commit()

    return RedirectResponse(url="/en/admin/users", status_code=302)