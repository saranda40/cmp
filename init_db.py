import asyncio
import sys
from src.database import engine
from src.models import Base

async def init_models():
    print("Conectando a PostgreSQL para crear las tablas del CMP...")
    try:
        async with engine.begin() as conn:
            # Crea todas las tablas mapeadas en src/models/__init__.py
            await conn.run_sync(Base.metadata.create_all)
        print("¡Perfecto! Las tablas se han creado con éxito en PostgreSQL.")
    except Exception as e:
        print(f"\n❌ Error al crear las tablas: {e}", file=sys.stderr)
        print("\n👉 Por favor, asegúrate de que:")
        print("   1. Tu servidor PostgreSQL esté corriendo.")
        print("   2. Hayas creado la base de datos vacía que especificaste en el .env.")
        print("   3. El usuario y la contraseña tengan permisos correctos.", file=sys.stderr)

if __name__ == "__main__":
    # Ejecuta el bucle asíncrono nativo
    asyncio.run(init_models())