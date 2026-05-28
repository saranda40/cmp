# Consent Management Platform (CMP) — Plataforma de Gestión de Consentimientos

Este proyecto es un motor centralizado (Backend) de alta velocidad diseñado en **FastAPI** y **PostgreSQL** para controlar el ciclo de vida, la inmutabilidad y la trazabilidad del uso de datos personales dentro de la empresa, garantizando el cumplimiento normativo de protección de datos.

---

## 🚀 Propósito Operativo (¿Qué problema resuelve?)

A diferencia de los sistemas de gestión documental tradicionales (que controlan facturas, cotizaciones o contratos), esta plataforma **no controla documentos, sino el uso de los datos personales**. Funciona como un **"filtro de legalidad"** en tiempo real para otros sistemas de la empresa (CRM, ERP, Sitios Web, etc.).

### Reglas de Negocio Implementadas:
* **Inmutabilidad Absoluta:** Los consentimientos otorgados o revocados por los usuarios nunca se editan ni se eliminan; el sistema mantiene un historial de auditoría de solo inserción (`INSERT`).
* **Control de Versiones:** Cada actualización de un texto legal genera una nueva versión. Al activarse una versión, las anteriores quedan marcadas automáticamente como obsoletas.
* **Filtro de Legalidad Activo:** Un consentimiento es **VÁLIDO** únicamente si el usuario aceptó explícitamente la **versión legal vigente**. Si el texto legal cambia con impactos de fondo, el estado pasa automáticamente a **OBSOLETO** obligando al sistema a solicitar un re-consentimiento.
* **Separación Contractual/Comercial:** El sistema no interfiere con operaciones legales u obligaciones contractuales (como emitir una factura o cotización), sino con usos secundarios que sí requieren consentimiento (Marketing, Analítica, Compartición con terceros).

---

## 🛠️ Arquitectura Técnica

El sistema está construido utilizando una arquitectura modular por capas con las siguientes tecnologías:

* **Python 3.12+**
* **FastAPI:** Framework de alto rendimiento para la exposición de endpoints e inyección de dependencias.
* **SQLAlchemy 2.0 (Async):** Mapeo objeto-relacional con soporte asíncrono nativo utilizando el driver `asyncpg`.
* **Pydantic v2:** Validación estricta de tipos y esquemas de entrada/salida de datos.
* **PostgreSQL:** Base de datos relacional robusta optimizada con índices estratégicos para consultas en tiempo real.

### Estructura del Modelo de Datos (Esquema):
* `purposes`: Catálogo de los fines de uso de datos (ej: `marketing`, `analytics`).
* `legal_documents`: Contenedor de los tipos de documentos legales (ej: `politica-privacidad`).
* `document_versions`: Historial y contenido exacto de los textos legales. Solo una versión está activa por documento.
* `consent_logs`: Tabla transaccional inmutable. Almacena las decisiones (`accepted`/`rejected`) con identificadores de usuario, marcas de tiempo, contextos de captura e IPs para auditorías.

---

## ⚙️ Instalación y Configuración

Sigue estos pasos para levantar el entorno de desarrollo localmente.

### 1. Clonar y Configurar el Entorno Virtual
```bash
# Crear entorno virtual
python3 -m venv .venv

# Activar el entorno virtual (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Activar el entorno virtual (Linux / macOS)
source .venv/bin/activate

# Actualizar herramientas de empaquetado e instalar dependencias
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt