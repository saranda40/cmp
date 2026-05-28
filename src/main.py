from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from src.config import settings
from src.database import get_db
from src.models.documents import LegalDocument, Purpose, DocumentVersion
from src.models.consents import ConsentLog, ConsentAction
from src.routers import legal, evaluation
from fastapi.staticfiles import StaticFiles

app = FastAPI(title=settings.PROJECT_NAME, version="1.0.0")
app.mount("/static", StaticFiles(directory="src/static"), name="static")

# Configuración del motor de plantillas Jinja2
templates = Jinja2Templates(directory="src/templates")

# Registro de Routers del Backend de la API
app.include_router(legal.router)
app.include_router(evaluation.router)


# --- 1. PANTALLA PRINCIPAL (HUB / HOME) ---
@app.get("/")
async def render_home(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="home.html", 
        context={}
    )


# --- 2. PANTALLA: FORMULARIO PÚBLICO Y FILTRO ---
@app.get("/form")
async def render_frontend(request: Request, db: AsyncSession = Depends(get_db)):
    # Obtener la versión activa del documento legal
    version_query = select(DocumentVersion).where(DocumentVersion.is_active == True).limit(1)
    version_result = await db.execute(version_query)
    active_version = version_result.scalar_one_or_none()

    # Obtener la lista de propósitos disponibles
    purposes_query = select(Purpose)
    purposes_result = await db.execute(purposes_query)
    purposes_list = purposes_result.scalars().all()

    return templates.TemplateResponse(
        request=request,
        name="form.html",
        context={
            "document": active_version, 
            "purposes": purposes_list
        }
    )


# --- 3. PANTALLA: PANEL DE ADMINISTRACIÓN (¡ARREGLADO!) ---
@app.get("/admin/management")  # <--- Faltaba este decorador clave
async def render_management(request: Request, db: AsyncSession = Depends(get_db)):
    # Traer todos los documentos existentes para listarlos en el select selectivo
    docs_query = select(LegalDocument)
    docs_result = await db.execute(docs_query)
    docs_list = docs_result.scalars().all()

    return templates.TemplateResponse(
        request=request,
        name="management.html",
        context={
            "documents": docs_list
        }
    )


# --- 4. RUTA DEL DASHBOARD DE AUDITORÍA ---
@app.get("/dashboard")
async def render_dashboard(request: Request, db: AsyncSession = Depends(get_db)):
    # Precargar las relaciones de forma asíncrona (selectinload)
    logs_query = (
        select(ConsentLog)
        .options(
            selectinload(ConsentLog.purpose),
            selectinload(ConsentLog.version)
        )
        .order_by(ConsentLog.created_at.desc())
        .limit(50)
    )
    logs_result = await db.execute(logs_query)
    logs_list = logs_result.scalars().all()

    # Calcular métricas de negocio en tiempo real
    total_logs = len(logs_list)
    
    accepted_query = select(func.count()).select_from(ConsentLog).where(ConsentAction.ACCEPTED == ConsentLog.action)
    accepted_res = await db.execute(accepted_query)
    total_accepted = accepted_res.scalar_one()

    rejected_query = select(func.count()).select_from(ConsentLog).where(ConsentAction.REJECTED == ConsentLog.action)
    rejected_res = await db.execute(rejected_query)
    total_rejected = rejected_res.scalar_one()

    users_query = select(func.count(func.distinct(ConsentLog.user_identifier)))
    users_res = await db.execute(users_query)
    total_users = users_res.scalar_one()

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "logs": logs_list,
            "total_logs": total_logs,
            "total_accepted": total_accepted,
            "total_rejected": total_rejected,
            "total_users": total_users
        }
    )