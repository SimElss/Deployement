from datetime import datetime
from sqlalchemy import DateTime, Table, Column, String, Integer, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
    
class Admins(Base):
    __tablename__ = 'admins'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    user: Mapped["Users"] = relationship("Users", back_populates="admin")
    
class Secretariats(Base):
    __tablename__ = 'secretariats'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    user: Mapped["Users"] = relationship("Users", back_populates="secretariat")

class respRecrutements(Base):
    __tablename__ = 'respRecrutements'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    user: Mapped["Users"] = relationship("Users", back_populates="respRecrutement")


class Users(Base):
    __tablename__ = 'users'
    id: Mapped[str] = mapped_column(String(72), primary_key=True)
    username: Mapped[str] = mapped_column(String(72), unique=True)
    name: Mapped[str] = mapped_column(String(72))
    surname: Mapped[str] = mapped_column(String(72))
    password: Mapped[str] = mapped_column(String(72))
    email: Mapped[str] = mapped_column(String(50), unique=True)
    group: Mapped[str] = mapped_column(String(7))
    whitelist: Mapped[bool] = mapped_column(Boolean)
    notification: Mapped[str] = mapped_column(String(255), default="")

    admin: Mapped["Admins"] = relationship("Admins", back_populates="user")
    secretariat: Mapped["Secretariats"] = relationship("Secretariats", back_populates="user")
    respRecrutement: Mapped["respRecrutements"] = relationship("respRecrutements", back_populates="user")
    dossiers: Mapped["DossierCandidats"] = relationship("DossierCandidats", back_populates="user")
    
class DossierCandidats(Base):
    __tablename__ = 'dossier_candidats'
    
    id: Mapped[str] = mapped_column(String(72), primary_key=True)
    username: Mapped[str] = mapped_column(String(72), nullable=False)
    name: Mapped[str] = mapped_column(String(72), nullable=False)
    mail: Mapped[str] = mapped_column(String(255), nullable=False)
    postereference: Mapped[str] = mapped_column(String(255), nullable=False)
    profref: Mapped[str] = mapped_column(String(255), nullable=False)
    phonenumber: Mapped[str] = mapped_column(String(15), nullable=False)
    image: Mapped[str] = mapped_column(String(255))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    
    details: Mapped["DetailsDossierCandidats"] = relationship("DetailsDossierCandidats", back_populates="dossier", uselist=False, cascade="all, delete-orphan", lazy="joined")
    user: Mapped["Users"] = relationship("Users", back_populates="dossiers")


class DetailsDossierCandidats(Base):
    __tablename__ = 'details_dossier_candidats'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    dossier_id: Mapped[str] = mapped_column(ForeignKey("dossier_candidats.id", ondelete="CASCADE"), unique=True, nullable=False)
    dossier: Mapped["DossierCandidats"] = relationship("DossierCandidats", back_populates="details")
    
    date_cloture: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    date_reception: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    dossier_complet: Mapped[bool] = mapped_column(Boolean, default=False)
    date_transmission_commission: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    date_reunion_commission: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    candidature_non_retenue: Mapped[str] = mapped_column(String(255), nullable=True)
    confirmation_information: Mapped[bool] = mapped_column(Boolean, default=False)
    date_entendu: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    position_classement: Mapped[int] = mapped_column(Integer, nullable=True)
    date_soumission_autorites: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    date_transmission_autorites: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    date_entree_fonction: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    date_suppression_dossier: Mapped[datetime] = mapped_column(DateTime, nullable=True)