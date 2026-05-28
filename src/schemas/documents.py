from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

# --- ESQUEMAS DE PROPÓSITOS (Purposes) ---
class PurposeBase(BaseModel):
    key: str = Field(..., max_length=50, examples=["marketing"])
    description: str = Field(..., max_length=255, examples=["Envío de ofertas y boletines comerciales"])

class PurposeCreate(PurposeBase):
    pass

class PurposeResponse(PurposeBase):
    id: int

    # En Pydantic v2, esto permite leer datos directamente desde modelos de SQLAlchemy
    model_config = ConfigDict(from_attributes=True)


# --- ESQUEMAS DE VERSIONES LEGALES (DocumentVersions) ---
class DocumentVersionBase(BaseModel):
    version_number: int = Field(..., gt=0, examples=[1])
    html_content: str = Field(..., examples=["<h1>Términos de Servicio v1</h1>..."])
    is_active: bool = Field(default=False)

class DocumentVersionCreate(DocumentVersionBase):
    document_id: int

class DocumentVersionResponse(DocumentVersionBase):
    id: int
    document_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- ESQUEMAS DE DOCUMENTOS LEGALES (LegalDocuments) ---
class LegalDocumentBase(BaseModel):
    name: str = Field(..., max_length=100, examples=["Políticas de Privacidad"])
    slug: str = Field(..., max_length=100, examples=["politica-privacidad"])

class LegalDocumentCreate(LegalDocumentBase):
    pass

class LegalDocumentResponse(LegalDocumentBase):
    id: int
    # Podemos incluir opcionalmente sus versiones si se solicitan
    versions: list[DocumentVersionResponse] = []

    model_config = ConfigDict(from_attributes=True)