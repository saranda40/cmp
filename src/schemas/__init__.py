from src.schemas.documents import (
    PurposeCreate, PurposeResponse, 
    LegalDocumentCreate, LegalDocumentResponse,
    DocumentVersionCreate, DocumentVersionResponse
)
from src.schemas.consents import (
    ConsentLogCreate, ConsentLogResponse, ConsentEvaluationResponse
)

__all__ = [
    "PurposeCreate", "PurposeResponse",
    "LegalDocumentCreate", "LegalDocumentResponse",
    "DocumentVersionCreate", "DocumentVersionResponse",
    "ConsentLogCreate", "ConsentLogResponse", "ConsentEvaluationResponse"
]