import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import AsyncSessionLocal, engine
from src.models.documents import Purpose, LegalDocument, DocumentVersion

async def seed_data():
    print("Inyectando datos iniciales de prueba...")
    
    async with AsyncSessionLocal() as session:
        async with session.begin():
            # 1. Crear Propósitos Básicos
            purposes = [
                Purpose(key="marketing", description="Envío de ofertas, promociones y boletines comerciales por email."),
                Purpose(key="analytics", description="Análisis de comportamiento de navegación para mejorar la plataforma."),
                Purpose(key="third_party", description="Compartir datos de contacto con socios comerciales estratégicos.")
            ]
            session.add_all(purposes)
            print("- Propósitos creados: marketing, analytics, third_party.")

            # 2. Crear Documento Legal (Términos y Condiciones)
            terms_doc = LegalDocument(
                name="Términos y Condiciones de Servicio",
                slug="terminos-servicio"
            )
            session.add(terms_doc)
            await session.flush() # Para obtener el ID del documento antes del commit

            # 3. Crear Versión 1 de este documento (Activa por defecto)
            v1 = DocumentVersion(
                document_id=terms_doc.id,
                version_number=1,
                html_content="<h3>Términos de Servicio v1</h3><p>Al usar este sitio aceptas que procesemos tus datos para operar el servicio contractual.</p>",
                is_active=True
            )
            session.add(v1)
            print("- Documento 'terminos-servicio' con Versión 1 (Activa) creada.")

    print("¡Datos inyectados con éxito!")

if __name__ == "__main__":
    asyncio.run(seed_data())