from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING, List
from sqlalchemy import String, Integer, Text, Boolean, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models.base import Base

if TYPE_CHECKING:
    from src.models.consents import ConsentLog
    
class Purpose(Base):
    __tablename__ = "purposes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)  # Ej: 'marketing'
    description: Mapped[str] = mapped_column(String(255), nullable=False)

    # Relación inversa con los logs de consentimiento
    consent_logs: Mapped[List["ConsentLog"]] = relationship("ConsentLog", back_populates="purpose")


class LegalDocument(Base):
    __tablename__ = "legal_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)  # Ej: 'politica-privacidad'

    # Relación con sus diferentes versiones
    versions: Mapped[List["DocumentVersion"]] = relationship("DocumentVersion", back_populates="document")


class DocumentVersion(Base):
    __tablename__ = "document_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("legal_documents.id", ondelete="CASCADE"), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)  # 1, 2, 3...
    html_content: Mapped[str] = mapped_column(Text, nullable=False)       # El texto legal exacto
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    # Relaciones
    document: Mapped["LegalDocument"] = relationship("LegalDocument", back_populates="versions")
    consent_logs: Mapped[List["ConsentLog"]] = relationship("ConsentLog", back_populates="version")