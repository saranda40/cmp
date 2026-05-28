from src.models.base import Base
from src.models.documents import Purpose, LegalDocument, DocumentVersion
from src.models.consents import ConsentLog, ConsentAction

# Esto facilita importar todo junto desde src.models
__all__ = ["Base", "Purpose", "LegalDocument", "DocumentVersion", "ConsentLog", "ConsentAction"]