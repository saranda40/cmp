from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from src.database import get_db
from src.models.consents import ConsentLog, ConsentAction
from src.models.documents import DocumentVersion, Purpose
from src.schemas.consents import ConsentLogCreate, ConsentLogResponse, ConsentEvaluationResponse

router = APIRouter(prefix="/evaluation", tags=["Motor de Evaluación y Consentimiento"])

# --- 1. REGISTRAR CONSENTIMIENTO (EVIDENCIA INMUTABLE) ---

@router.post("/consent", response_model=ConsentLogResponse, status_code=status.HTTP_201_CREATED)
async def register_consent(consent_data: ConsentLogCreate, db: AsyncSession = Depends(get_db)):
    # Validar que el propósito exista
    purpose_query = select(Purpose).where(Purpose.id == consent_data.purpose_id)
    purpose_result = await db.execute(purpose_query)
    if not purpose_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="El propósito especificado no existe.")

    # Validar que la versión del documento exista
    version_query = select(DocumentVersion).where(DocumentVersion.id == consent_data.version_id)
    version_result = await db.execute(version_query)
    if not version_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="La versión del documento legal no existe.")

    # Insertar el registro (Inmutabilidad: No modificamos nada, siempre agregamos historial)
    db_log = ConsentLog(**consent_data.model_dump())
    db.add(db_log)
    await db.commit()
    await db.refresh(db_log)
    return db_log


# --- 2. EL FILTRO DE LEGALIDAD EN TIEMPO REAL ---

@router.get("/verify", response_model=ConsentEvaluationResponse)
async def verify_consent(
    user_identifier: str = Query(..., examples=["usuario@email.com"]),
    purpose_key: str = Query(..., examples=["marketing"]),
    db: AsyncSession = Depends(get_db)
):
    # 1. Buscar el propósito por su llave (ej: 'marketing')
    purpose_query = select(Purpose).where(Purpose.key == purpose_key)
    purpose_res = await db.execute(purpose_query)
    purpose = purpose_res.scalar_one_or_none()
    
    if not purpose:
        raise HTTPException(status_code=404, detail=f"El propósito '{purpose_key}' no está registrado.")

    # 2. Buscar la última decisión del usuario para este propósito en específico
    consent_query = (
        select(ConsentLog)
        .where(ConsentLog.user_identifier == user_identifier, ConsentLog.purpose_id == purpose.id)
        .order_by(desc(ConsentLog.created_at))
        .limit(1)
    )
    consent_res = await db.execute(consent_query)
    last_consent = consent_res.scalar_one_or_none()

    # REGLA 1: Si no hay registros de decisión -> INEXISTENTE
    if not last_consent:
        return ConsentEvaluationResponse(
            user_identifier=user_identifier,
            purpose_key=purpose_key,
            status="inexistente",
            allowed=False
        )

    # REGLA 2: Si el usuario rechazó explícitamente -> RECHAZADO
    if last_consent.action == ConsentAction.REJECTED:
        return ConsentEvaluationResponse(
            user_identifier=user_identifier,
            purpose_key=purpose_key,
            status="rechazado",
            allowed=False
        )

    # REGLA 3: Si aceptó, debemos verificar si la versión que aceptó sigue vigente
    # Para esto, buscamos cuál es la versión activa del documento asociado a ese consentimiento
    version_query = select(DocumentVersion).where(DocumentVersion.id == last_consent.version_id)
    version_res = await db.execute(version_query)
    accepted_version = version_res.scalar_one_or_none()

    # Buscamos la versión que actualmente está activa para ese mismo documento base
    active_version_query = (
        select(DocumentVersion)
        .where(DocumentVersion.document_id == accepted_version.document_id, DocumentVersion.is_active == True)
    )
    active_version_res = await db.execute(active_version_query)
    current_active_version = active_version_res.scalar_one_or_none()

    # Si la versión que aceptó coincide con la versión activa actual -> VÁLIDO
    if current_active_version and last_consent.version_id == current_active_version.id:
        return ConsentEvaluationResponse(
            user_identifier=user_identifier,
            purpose_key=purpose_key,
            status="valido",
            allowed=True
        )
    
    # REGLA 4: Si aceptó pero la versión actual es más nueva -> OBSOLETO
    return ConsentEvaluationResponse(
        user_identifier=user_identifier,
        purpose_key=purpose_key,
        status="obsoleto",
        allowed=False
    )