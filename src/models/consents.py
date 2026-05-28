from __future__ import annotations  # <--- PRIMERA LÍNEA OBLIGATORIA
import uuid
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, ForeignKey, DateTime, func, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from src.models.base import Base

if TYPE_CHECKING:
    from src.models.documents import DocumentVersion, Purpose

class ConsentAction(str, enum.Enum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"

class ConsentLog(Base):
    __tablename__ = "consent_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_identifier: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    
    version_id: Mapped[int] = mapped_column(ForeignKey("document_versions.id"), nullable=False)
    purpose_id: Mapped[int] = mapped_column(ForeignKey("purposes.id"), nullable=False)
    
    action: Mapped[ConsentAction] = mapped_column(Enum(ConsentAction), nullable=False)
    context: Mapped[str] = mapped_column(String(100), nullable=False)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False, index=True)

    # Quitamos comillas aquí también
    version: Mapped[DocumentVersion] = relationship("DocumentVersion", back_populates="consent_logs")
    purpose: Mapped[Purpose] = relationship("Purpose", back_populates="consent_logs")