from typing import Optional, List
from uuid import uuid4
from sqlalchemy import select, func
from ..database import Session
from ..models.models import DossierCandidats, DetailsDossierCandidats, Users
from datetime import date, datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from sqlalchemy.orm import joinedload
from msal import ConfidentialClientApplication

def get_dossier_by_id(id: str) -> (Optional[DossierCandidats], bool): # type: ignore
    """
    Retrieves a dossier by its ID, including its associated details.
    Also returns an indicator if the dossier has missing details.

    Args:
        id (str): The ID of the dossier to retrieve.

    Returns:
        tuple: A tuple containing the dossier and a boolean (True if the dossier has missing details, False otherwise).
    """
    with Session() as session:
        dossier = session.query(DossierCandidats).options(joinedload(DossierCandidats.details)).filter_by(id=id).first()
        has_missing_details = dossier.details is None if dossier else False
        return dossier, has_missing_details
    
def get_details_dossier_by_id(dossier_id: str):
    """
    Retrieves the details of a dossier by its ID.

    Args:
        dossier_id (str): The ID of the dossier.

    Returns:
        DetailsDossierCandidats: The details of the corresponding dossier.
    """
    with Session() as session:
        return session.query(DetailsDossierCandidats).filter_by(dossier_id=dossier_id).first()
    
def get_dossiers_by_candidat(user_id: str, page: int, per_page: int) -> (List[DossierCandidats], bool): # type: ignore
    """
    Retrieves dossiers associated with a user, with pagination.
    Also returns an indicator if any dossiers have missing details.

    Args:
        user_id (str): The ID of the user.
        page (int): The page number.
        per_page (int): The number of dossiers per page.

    Returns:
        tuple: A list of dossiers and a boolean (True if any dossiers have missing details, False otherwise).
    """
    with Session() as session:
        dossiers = session.query(DossierCandidats).options(joinedload(DossierCandidats.details)).filter_by(user_id=user_id).offset((page - 1) * per_page).limit(per_page).all()
        has_missing_details = any(dossier.details is None for dossier in dossiers)
        return dossiers, has_missing_details
    
def update_dossier(dossier_id: str, name: str, mail: str, phonenumber: str, postereference: str) -> bool:
    """
    Updates the information of a dossier in the database.

    Args:
        dossier_id (str): The ID of the dossier to update.
        name (str): The new name.
        mail (str): The new email.
        phonenumber (str): The new phone number.
        postereference (str): The new position reference.

    Returns:
        bool: True if the update was successful, False otherwise.
    """
    with Session() as session:
        dossier = session.query(DossierCandidats).filter(DossierCandidats.id == dossier_id).first()
        if not dossier:
            return False

        dossier.name = name
        dossier.mail = mail
        dossier.phonenumber = phonenumber
        dossier.postereference = postereference

        session.commit()
        return True

def update_dossier_details(
    dossier_id: str,
    mail: str,
    phonenumber: str,
    date_cloture: str,
    date_reception: str,
    dossier_complet: str,
    date_transmission_commission: str = None,
    date_reunion_commission: str = None,
    candidature_non_retenue: str = None,
    confirmation_information: str = None,
    date_entendu: str = None,
    position_classement: int = None,
    date_soumission_autorites: str = None,
    date_transmission_autorites: str = None,
    date_entree_fonction: str = None,
    date_suppression_dossier: str = None
) -> bool:
    """
    Updates the details of a dossier in the database.

    Args:
        dossier_id (str): The ID of the dossier.
        mail (str): The new email.
        phonenumber (str): The new phone number.
        date_cloture (str): The closing date.
        date_reception (str): The reception date.
        dossier_complet (str): Whether the dossier is complete.
        date_transmission_commission (str): The transmission date to the commission.
        date_reunion_commission (str): The commission meeting date.
        candidature_non_retenue (str): Whether the application was not retained.
        confirmation_information (str): Whether the information is confirmed.
        date_entendu (str): The hearing date.
        position_classement (int): The ranking position.
        date_soumission_autorites (str): The submission date to authorities.
        date_transmission_autorites (str): The transmission date to authorities.
        date_entree_fonction (str): The start date.
        date_suppression_dossier (str): The dossier deletion date.

    Returns:
        bool: True if the update was successful, False otherwise.
    """
    with Session() as session:
        dossier = session.query(DossierCandidats).filter_by(id=dossier_id).first()
        details = session.query(DetailsDossierCandidats).filter_by(dossier_id=dossier_id).first()
        if dossier and details:
            dossier.mail = mail
            dossier.phonenumber = phonenumber
            
            details.date_cloture = datetime.strptime(date_cloture, '%Y-%m-%d') if date_cloture else None
            details.date_reception = datetime.strptime(date_reception, '%Y-%m-%d') if date_reception else None
            details.date_transmission_commission = datetime.strptime(date_transmission_commission, '%Y-%m-%d') if date_transmission_commission else None
            details.date_reunion_commission = datetime.strptime(date_reunion_commission, '%Y-%m-%d') if date_reunion_commission else None
            details.date_entendu = datetime.strptime(date_entendu, '%Y-%m-%d') if date_entendu else None
            details.date_soumission_autorites = datetime.strptime(date_soumission_autorites, '%Y-%m-%d') if date_soumission_autorites else None
            details.date_transmission_autorites = datetime.strptime(date_transmission_autorites, '%Y-%m-%d') if date_transmission_autorites else None
            details.date_entree_fonction = datetime.strptime(date_entree_fonction, '%Y-%m-%d') if date_entree_fonction else None
            details.date_suppression_dossier = datetime.strptime(date_suppression_dossier, '%Y-%m-%d') if date_suppression_dossier else None
            
            
            details.dossier_complet = dossier_complet == "True"
            details.candidature_non_retenue = candidature_non_retenue == "True"
            details.confirmation_information = confirmation_information == "True"
            
            
            details.position_classement = position_classement
            
            session.commit()
            return True
        return False
    
def search_dossiers(keyword: str, page: int = 1, per_page: int = 10) -> (List[DossierCandidats], bool): # type: ignore
    """
    Searches for dossiers based on a keyword using strict equality.
    The search is performed on relevant fields such as email, phone number, or position reference.
    Also returns an indicator if any records have missing details.

    Args:
        keyword (str): The keyword to search for.
        page (int): The page number.
        per_page (int): The number of dossiers per page.

    Returns:
        tuple: A list of dossiers and a boolean (True if any dossiers have missing details, False otherwise).
    """
    with Session() as session:
        query = session.query(DossierCandidats).filter(
            (DossierCandidats.mail == keyword) |
            (DossierCandidats.phonenumber == keyword) |
            (DossierCandidats.postereference == keyword) |
            (DossierCandidats.name == keyword)  # Exemple pour une colonne "nom"
        )
        # Pagination
        dossiers = query.offset((page - 1) * per_page).limit(per_page).all()
        has_missing_details = any(dossier.details is None for dossier in dossiers)
        return dossiers, has_missing_details
    
def add_dossier_candidat(username: str, name: str, mail: str, postereference: str, profref: str, phonenumber: str, image: str, user_id: str) -> DossierCandidats:
    """
    Adds a new candidate dossier to the database.

    Args:
        username (str): The username of the candidate.
        name (str): The name of the candidate.
        mail (str): The email of the candidate.
        postereference (str): The position reference.
        profref (str): The referring professor.
        phonenumber (str): The phone number of the candidate.
        image (str): The image link.
        user_id (str): The ID of the user.

    Returns:
        DossierCandidats: The newly created dossier.
    """
    new_dossier = DossierCandidats(
        id=str(uuid4()),
        username=username,
        name=name,
        mail=mail,
        postereference=postereference,
        profref=profref,
        phonenumber=phonenumber,
        image=image,
        user_id=user_id
    )
    with Session() as session:
        session.add(new_dossier)
        session.commit()
        session.refresh(new_dossier)
    return new_dossier


def add_details_dossier_candidat(
    dossier_id: str,
    date_cloture: Optional[str] = None,
    date_reception: Optional[str] = None,
    dossier_complet: bool = False,
    date_transmission_commission: Optional[str] = None,
    date_reunion_commission: Optional[str] = None,
    candidature_non_retenue: bool = False,
    confirmation_information: bool = False,
    date_entendu: Optional[str] = None,
    position_classement: Optional[int] = None,
    date_soumission_autorites: Optional[str] = None,
    date_transmission_autorites: Optional[str] = None,
    date_entree_fonction: Optional[str] = None,
    date_suppression_dossier: Optional[str] = None
) -> DetailsDossierCandidats:
    """
    Adds the details of a candidate dossier to the database.

    Args:
        dossier_id (str): The ID of the dossier.
        date_cloture (str): The closing date.
        date_reception (str): The reception date.
        dossier_complet (bool): Whether the dossier is complete.
        date_transmission_commission (str): The transmission date to the commission.
        date_reunion_commission (str): The commission meeting date.
        candidature_non_retenue (bool): Whether the application was not retained.
        confirmation_information (bool): Whether the information is confirmed.
        date_entendu (str): The hearing date.
        position_classement (int): The ranking position.
        date_soumission_autorites (str): The submission date to authorities.
        date_transmission_autorites (str): The transmission date to authorities.
        date_entree_fonction (str): The start date.
        date_suppression_dossier (str): The dossier deletion date.

    Returns:
        DetailsDossierCandidats: The newly created dossier details.
    """

    # Fonction pour convertir une chaîne de caractères en objet date
    def parse_date(date_str: Optional[str]) -> Optional[date]:
        return datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else None

    new_details = DetailsDossierCandidats(
        dossier_id=dossier_id,
        date_cloture=parse_date(date_cloture),
        date_reception=parse_date(date_reception),
        dossier_complet=dossier_complet,
        date_transmission_commission=parse_date(date_transmission_commission),
        date_reunion_commission=parse_date(date_reunion_commission),
        candidature_non_retenue=candidature_non_retenue,
        confirmation_information=confirmation_information,
        date_entendu=parse_date(date_entendu),
        position_classement=position_classement,
        date_soumission_autorites=parse_date(date_soumission_autorites),
        date_transmission_autorites=parse_date(date_transmission_autorites),
        date_entree_fonction=parse_date(date_entree_fonction),
        date_suppression_dossier=parse_date(date_suppression_dossier)
    )
    with Session() as session:
        session.add(new_details)
        session.commit()
        session.refresh(new_details)
    return new_details

def delete_candidat(candidat_id: str) -> bool:
    """
    Deletes a candidate dossier from the database.

    Args:
        candidat_id (str): The ID of the candidate dossier to delete.

    Returns:
        bool: True if the deletion was successful, False otherwise.
    """
    with Session() as session:
        candidat = session.query(DossierCandidats).filter(DossierCandidats.id == candidat_id).first()
        
        session.delete(candidat)
        session.commit()
        return True



