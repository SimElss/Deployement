from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from uuid import uuid4
import hashlib
from datetime import datetime

engine = create_engine(
    "sqlite:///data/db.sqlite",  # Path to the database file
    echo=False,  # Show generated SQL code in the terminal
)
Session = sessionmaker(engine)

class Base(DeclarativeBase):
    pass

from app.models.models import Base, DossierCandidats, Users, respRecrutements, Secretariats, Admins, DetailsDossierCandidats

def delete_database():
    """
    Clear all table definitions from the metadata.
    """
    Base.metadata.clear()

def create_database():
    """
    Create all tables in the database.
    """
    Base.metadata.create_all(engine)

def vider_db():
    """
    Delete all records from all tables in the database.
    """
    session = Session()
    try:
        # Delete all records from each table
        session.query(Users).delete()
        session.query(Admins).delete()
        session.query(Secretariats).delete()
        session.query(respRecrutements).delete()
        session.query(DossierCandidats).delete()
        session.query(DetailsDossierCandidats).delete()
        session.commit()
    except Exception as e:
        print(f"Error while emptying the database: {e}")
        session.rollback()
    finally:
        session.close()

def initialiser_db():
    """
    Initialize the database with initial data if the tables are empty.
    """
    with Session() as session:
        # Check if the Users table is already populated
        if session.query(Users).count() == 0:
            # Create passwords and hash them
            password_1 = "Admin!123"
            password_2 = "Password!123"
            password_3 = "Password!123"
            password_4 = "Password!123"
            encoded_password_1 = password_1.encode()
            hashed_password_1 = hashlib.sha3_256(encoded_password_1).hexdigest()

            encoded_password_2 = password_2.encode()
            hashed_password_2 = hashlib.sha3_256(encoded_password_2).hexdigest()

            encoded_password_3 = password_3.encode()
            hashed_password_3 = hashlib.sha3_256(encoded_password_3).hexdigest()
            
            encoded_password_4 = password_4.encode()
            hashed_password_4 = hashlib.sha3_256(encoded_password_4).hexdigest()

            # Create users
            user_1 = Users(id=str(uuid4()), username="admin", name="admin", surname="admin", password=hashed_password_1, email="admin@juice-sh.op", group="admin", whitelist=True, notification="")
            
            user_2 = Users(id=str(uuid4()), username="User2", name="Doe", surname="John", password=hashed_password_2, email="user@gmail.com", group="candidat", whitelist=True,  notification="Vous avez été sélectionné pour le poste de secrétaire !")
            user_6 = Users(id=str(uuid4()), username="User6", name="Eve", surname="Williams", password=hashed_password_2, email="user1@gmail.com", group="candidat", whitelist=True, notification="")
            user_7 = Users(id=str(uuid4()), username="User7", name="Charlie", surname="Brown", password=hashed_password_2, email="user3@gmail.com", group="candidat", whitelist=True, notification="")

            user_3 = Users(id=str(uuid4()), username="User3", name="Doe", surname="John", password=hashed_password_3, email="secretariat@gmail.com", group="secretariat", whitelist=True, notification="")
            user_4 = Users(id=str(uuid4()), username="User4", name="Elice", surname="Simon", password=hashed_password_4, email="resp@gmail.com", group="respRecrutement", whitelist=True, notification="")
            user_5 = Users(id=str(uuid4()), username="User5", name="Michael", surname="John", password=hashed_password_2, email="user2@gmail.com", group="candidat", whitelist=True, notification="")

            # Create admin
            admin_1 = Admins(id=1, user_id=user_1.id)
            secretariat_1 = Secretariats(id=3, user_id=user_3.id)
            respRecrutement_1 = respRecrutements(id=4, user_id=user_4.id)

            # Create folder candidat

            candidate_1 = DossierCandidats(id=str(uuid4()), username="John", name="Doe", mail="candidate1@gmail.com", postereference="Z50007300" , profref="Mr.Schumacher",phonenumber="+32472456891", image="../static/images/image1.jpeg", user_id=user_2.id)
            candidate_2 = DossierCandidats(id=str(uuid4()), username="John", name="Doe", mail="elicesimon06@gmail.com", postereference="Z50007301", profref="Mr.Frenay",phonenumber="+32472456891", image="../static/images/image1.jpeg", user_id=user_2.id)
            candidate_3 = DossierCandidats(id=str(uuid4()), username="Eve", name="Williams", mail="candidate1@gmail.com", postereference="Z50007303" , profref="Mr.Elice",phonenumber="+32477129438", image="../static/images/image2.jpg", user_id=user_6.id)
            candidate_4 = DossierCandidats(id=str(uuid4()), username="Charlie", name="Brown", mail="candidate2@gmail.com", postereference="50001235", profref="Mr.Englebert",phonenumber="+32489567024", image="../static/images/image3.jpg", user_id=user_7.id)
            candidate_5 = DossierCandidats(id=str(uuid4()), username="John", name="Doe", mail="candidate1@gmail.com", postereference="50001235" , profref="Mr.Benoit",phonenumber="+32472456891", image="../static/images/image1.jpeg", user_id=user_2.id)
            candidate_6 = DossierCandidats(id=str(uuid4()), username="John", name="Doe", mail="candidate2@gmail.com", postereference="50001232", profref="Mr.Xavier",phonenumber="+32472456891", image="../static/images/image1.jpeg", user_id=user_2.id)

            # Create details for folder candidat
            details_candidate_1 = DetailsDossierCandidats(
                dossier_id=candidate_1.id,
                date_cloture=datetime(2025, 12, 31),
                date_reception=datetime(2025, 1, 1),
                dossier_complet=True,
                date_transmission_commission=datetime(2025, 2, 1),
                date_reunion_commission=datetime(2025, 3, 1),
                candidature_non_retenue=False,
                confirmation_information=True,
                date_entendu=datetime(2025, 4, 1),
                position_classement=1,
                date_soumission_autorites=datetime(2025, 5, 1),
                date_transmission_autorites=datetime(2025, 6, 1),
                date_entree_fonction=datetime(2025, 7, 1),
                date_suppression_dossier=datetime(2026, 1, 1)
            )

            details_candidate_2 = DetailsDossierCandidats(
                dossier_id=candidate_2.id,
                date_cloture=datetime(2025, 12, 31),
                date_reception=datetime(2025, 1, 1),
                dossier_complet=True,
                date_transmission_commission=datetime(2025, 2, 1),
                date_reunion_commission=datetime(2025, 3, 1),
                candidature_non_retenue=False,
                confirmation_information=True,
                date_entendu=datetime(2025, 4, 1),
                position_classement=2,
                date_soumission_autorites=datetime(2025, 5, 1),
                date_transmission_autorites=datetime(2025, 6, 1),
                date_entree_fonction=datetime(2025, 7, 1),
                date_suppression_dossier=datetime(2026, 1, 1)
            )


             # Ajouter les candidats et leurs détails uniquement s'ils n'existent pas déjà
            session.add_all([user_1, user_2, user_3, user_4, user_5, admin_1, secretariat_1, respRecrutement_1])
            session.add_all([candidate_1, candidate_2, candidate_3, candidate_4, candidate_5, candidate_6])
            session.add_all([details_candidate_1, details_candidate_2])

            session.commit()
            