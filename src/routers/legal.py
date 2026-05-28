from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from src.database import get_db
from src.models.documents import Purpose, LegalDocument, DocumentVersion
from src.schemas.documents import (
    PurposeCreate, PurposeResponse,
    LegalDocumentCreate, LegalDocumentResponse,
    DocumentVersionCreate, DocumentVersionResponse
)

router = APIRouter(prefix="/legal", tags=["Gestión Legal"])

# --- ENDPOINTS PARA PROPÓSITOS (Purposes) ---

@router.post("/purposes", response_model=PurposeResponse, status_code=status.HTTP_201_CREATED)
async def create_purpose(purpose_data: PurposeCreate, db: AsyncSession = Depends(get_db)):
    # Verificar si ya existe la llave del propósito
    query = select(Purpose).where(Purpose.key == purpose_data.key)
    result = await db.execute(query)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El propósito con la llave '{purpose_data.key}' ya existe."
        )
    
    db_purpose = Purpose(**purpose_data.model_dump())
    db.add(db_purpose)
    await db.commit()
    await db.refresh(db_purpose)
    return db_purpose


@router.get("/purposes", response_model=list[PurposeResponse])
async def list_purposes(db: AsyncSession = Depends(get_db)):
    query = select(Purpose)
    result = await db.execute(query)
    return result.scalars().all()


# --- ENDPOINTS PARA DOCUMENTOS (LegalDocuments) ---

@router.post("/documents", response_model=LegalDocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(doc_data: LegalDocumentCreate, db: AsyncSession = Depends(get_db)):
    # Verificar si el slug ya existe
    query = select(LegalDocument).where(LegalDocument.slug == doc_data.slug)
    result = await db.execute(query)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El documento con el slug '{doc_data.slug}' ya existe."
        )
    
    db_doc = LegalDocument(**doc_data.model_dump())
    db.add(db_doc)
    await db.commit()
    await db.refresh(db_doc)
    return db_doc


# --- ENDPOINTS PARA VERSIONES (DocumentVersions) ---

@router.post("/versions", response_model=DocumentVersionResponse, status_code=status.HTTP_201_CREATED)
async def create_document_version(version_data: DocumentVersionCreate, db: AsyncSession = Depends(get_db)):
    # 1. Validar que el documento base exista
    doc_query = select(LegalDocument).where(LegalDocument.id == version_data.document_id)
    doc_result = await db.execute(doc_query)
    if not doc_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El documento legal especificado no existe."
        )

    # 2. Si la nueva versión viene como activa, desactivamos todas las anteriores de ese documento
    if version_data.is_active:
        await db.execute(
            update(DocumentVersion)
            .where(DocumentVersion.document_id == version_data.document_id)
            .values(is_active=False)
        )

    # 3. Insertar la nueva versión
    db_version = DocumentVersion(**version_data.model_dump())
    db.add(db_version)
    
    await db.commit()
    await db.refresh(db_version)
    return db_version