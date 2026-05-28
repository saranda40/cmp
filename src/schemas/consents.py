from datetime import datetime
import uuid
from pydantic import BaseModel, ConfigDict, Field, EmailStr
from src.models.consents import ConsentAction

class ConsentLogCreate(BaseModel):
    # Identificador único del usuario (ej: email o ID interno del CRM)
    user_identifier: str = Field(..., max_length=150, examples=["usuario@email.com"])
    version_id: int = Field(..., examples=[1])
    purpose_id: int = Field(..., examples=[2])
    action: ConsentAction = Field(..., examples=[ConsentAction.ACCEPTED])
    context: str = Field(..., max_length=100, examples=["web_checkout"])
    ip_address: str | None = Field(default=None, max_length=45, examples=["192.168.1.1"])

class ConsentLogResponse(BaseModel):
    id: uuid.UUID
    user_identifier: str
    version_id: int
    purpose_id: int
    action: ConsentAction
    context: str
    ip_address: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- ESQUEMA DE EVALUACIÓN (El "Filtro de Legalidad" en tiempo real) ---
# Este esquema sirve para responder cuando un sistema externo pregunta si puede usar un dato.
class ConsentEvaluationResponse(BaseModel):
    user_identifier: str
    purpose_key: str
    # Los estados posibles que definiste en tu resumen: válido, obsoleto, rechazado, inexistente
    status: str = Field(..., examples=["valido", "obsoleto", "rechazado", "inexistente"])
    allowed: bool = Field(..., description="Indica explícitamente si el sistema puede o no usar el dato")