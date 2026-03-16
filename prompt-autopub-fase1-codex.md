# Auto Publisher — FASE 1: Backend Base + Generación de Texto con IA

## CONTEXTO
Estás construyendo un sistema de publicación automatizada en redes sociales. Este es un proyecto NUEVO. El repo está en: https://github.com/Aldairmm18/auto-publisher.git

Este archivo contiene TODAS las instrucciones para la Fase 1. Lee TODO antes de escribir código.

---

## PASO 1: Crear estructura de carpetas

Crea esta estructura exacta en la raíz del proyecto:

```
auto-publisher/
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── models.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ai_text.py
│   │   └── storage.py
│   ├── publishers/
│   │   ├── __init__.py
│   │   └── base.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── supabase_client.py
│   │   └── posts.py
│   ├── requirements.txt
│   └── .env.example
├── supabase/
│   └── migrations/
│       └── 001_auto_publisher.sql
├── .gitignore
└── README.md
```

Ejecuta estos comandos para crear las carpetas:
```bash
mkdir -p backend/services backend/publishers backend/database supabase/migrations
touch backend/__init__.py backend/services/__init__.py backend/publishers/__init__.py backend/database/__init__.py
```

---

## PASO 2: Crear .gitignore

Crear archivo `.gitignore` en la RAÍZ del proyecto con este contenido exacto:

```
# Python
__pycache__/
*.py[cod]
*.pyo
*.egg-info/
dist/
build/
venv/
.venv/
env/

# Environment
.env
.env.local
.env.production

# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Node (para frontend futuro)
node_modules/
.next/
```

---

## PASO 3: Crear backend/requirements.txt

```
fastapi==0.115.0
uvicorn[standard]==0.30.0
python-dotenv==1.0.1
google-genai==1.14.0
supabase==2.28.0
python-telegram-bot==22.6
python-multipart==0.0.9
aiofiles==24.1.0
```

---

## PASO 4: Crear backend/.env.example

```
# Supabase
SUPABASE_URL=https://scvltqqtkjazopjyauyv.supabase.co
SUPABASE_SERVICE_KEY=tu_service_role_key_aqui

# Google AI (Gemini)
GEMINI_API_KEY=tu_gemini_api_key_aqui

# Telegram Bot (para fases futuras)
TELEGRAM_BOT_TOKEN=tu_token_aqui
```

---

## PASO 5: Crear backend/config.py

Este archivo carga las variables de entorno. Escríbelo así:

```python
"""
Configuración central del Auto Publisher.
Carga variables de entorno desde .env
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")

# Gemini AI
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# Validación
def validate_config():
    """Verifica que las variables críticas estén presentes."""
    missing = []
    if not SUPABASE_URL:
        missing.append("SUPABASE_URL")
    if not SUPABASE_SERVICE_KEY:
        missing.append("SUPABASE_SERVICE_KEY")
    if not GEMINI_API_KEY:
        missing.append("GEMINI_API_KEY")
    if missing:
        print(f"⚠️  Variables faltantes: {', '.join(missing)}")
        print("   Copia .env.example a .env y llena los valores.")
    return len(missing) == 0
```

---

## PASO 6: Crear backend/database/supabase_client.py

```python
"""
Cliente de Supabase para el Auto Publisher.
Usa la service_role key para bypass de RLS.
"""

from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_SERVICE_KEY

supabase: Client | None = None

if SUPABASE_URL and SUPABASE_SERVICE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
else:
    print("⚠️  Supabase no configurado. El backend funcionará sin base de datos.")
```

---

## PASO 7: Crear backend/database/posts.py

```python
"""
CRUD de posts en Supabase.
"""

from datetime import datetime
from database.supabase_client import supabase


async def crear_post(user_id: str, title: str, content: str, media_type: str | None = None) -> dict:
    """Crea un post en estado draft."""
    if not supabase:
        raise RuntimeError("Supabase no disponible")
    
    row = {
        "user_id": user_id,
        "title": title,
        "content_original": content,
        "media_type": media_type,
        "status": "draft",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }
    result = supabase.table("posts").insert(row).execute()
    if not result.data:
        raise RuntimeError("Error al crear post en Supabase")
    return result.data[0]


async def crear_variante(post_id: str, platform: str, generated_text: str, hashtags: str = "") -> dict:
    """Crea una variante de texto para una plataforma específica."""
    if not supabase:
        raise RuntimeError("Supabase no disponible")
    
    row = {
        "post_id": post_id,
        "platform": platform,
        "generated_text": generated_text,
        "hashtags": hashtags,
        "caption": generated_text,  # Por defecto el caption es el texto generado
        "status": "pending",
        "created_at": datetime.utcnow().isoformat(),
    }
    result = supabase.table("post_variants").insert(row).execute()
    if not result.data:
        raise RuntimeError(f"Error al crear variante para {platform}")
    return result.data[0]


async def obtener_post(post_id: str) -> dict | None:
    """Obtiene un post por su ID con sus variantes."""
    if not supabase:
        return None
    
    result = supabase.table("posts").select("*").eq("id", post_id).maybe_single().execute()
    if not result.data:
        return None
    
    post = result.data
    variants = supabase.table("post_variants").select("*").eq("post_id", post_id).execute()
    post["variants"] = variants.data or []
    return post


async def listar_posts(user_id: str, limit: int = 20) -> list:
    """Lista los posts más recientes de un usuario."""
    if not supabase:
        return []
    
    result = (
        supabase.table("posts")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return result.data or []


async def actualizar_estado_post(post_id: str, status: str) -> dict | None:
    """Actualiza el estado de un post."""
    if not supabase:
        return None
    
    result = (
        supabase.table("posts")
        .update({"status": status, "updated_at": datetime.utcnow().isoformat()})
        .eq("id", post_id)
        .execute()
    )
    return result.data[0] if result.data else None
```

---

## PASO 8: Crear backend/models.py

```python
"""
Modelos Pydantic para request/response del API.
"""

from pydantic import BaseModel
from typing import Optional


class GenerateTextRequest(BaseModel):
    """Request para generar texto para redes sociales."""
    tema: str                          # Ej: "Tutorial de edición en Premiere Pro"
    descripcion: Optional[str] = None  # Descripción adicional opcional
    tono: str = "profesional"          # profesional, casual, divertido, inspirador
    idioma: str = "es"                 # es = español


class GenerateTextResponse(BaseModel):
    """Response con texto generado para cada plataforma."""
    facebook: str
    instagram: str
    tiktok: str
    youtube_title: str
    youtube_description: str
    youtube_tags: list[str]


class CreatePostRequest(BaseModel):
    """Request para crear un post completo."""
    titulo: str
    descripcion: str
    tono: str = "profesional"
    plataformas: list[str] = ["facebook", "instagram", "tiktok", "youtube"]


class PostResponse(BaseModel):
    """Response de un post creado."""
    post_id: str
    status: str
    variantes: dict  # {platform: generated_text}
```

---

## PASO 9: Crear backend/services/ai_text.py

ESTE ES EL ARCHIVO MÁS IMPORTANTE DE ESTA FASE. Lee las instrucciones con cuidado.

```python
"""
Servicio de generación de texto con Gemini AI.
Genera texto optimizado para cada red social.
"""

from google import genai
from config import GEMINI_API_KEY

# Inicializar cliente de Gemini
client = None
if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)
else:
    print("⚠️  GEMINI_API_KEY no configurada. La generación de texto no funcionará.")


SYSTEM_PROMPT = """Eres un experto en marketing digital y redes sociales. 
Tu trabajo es generar texto optimizado para publicaciones en redes sociales.
Siempre respondes en español (Colombia).
El texto debe ser atractivo, natural, y adaptado al estilo de cada plataforma.
NO uses lenguaje genérico ni frases cliché como "no te lo pierdas" o "descubre más".
Sé creativo, auténtico, y directo."""


def _build_prompt(tema: str, descripcion: str | None, tono: str, platform: str) -> str:
    """Construye el prompt específico para cada plataforma."""
    
    platform_instructions = {
        "facebook": """Genera un post para FACEBOOK.
- Texto de 2-4 párrafos (150-300 palabras)
- Tono conversacional pero informativo
- Incluye 1-2 emojis relevantes (no exageres)
- Termina con una pregunta o call-to-action para generar interacción
- NO incluyas hashtags (Facebook no los necesita)""",
        
        "instagram": """Genera un caption para INSTAGRAM.
- Máximo 2200 caracteres
- Primera línea debe ser un hook que atrape (máx 125 chars antes del "más...")
- Cuerpo del texto con valor real
- Incluye emojis distribuidos naturalmente
- Al final: bloque de 15-20 hashtags relevantes en español, separados por espacios
- Los hashtags deben ser una mezcla de populares y de nicho""",
        
        "tiktok": """Genera una descripción para TIKTOK.
- Máximo 300 caracteres (esto es MUY corto, sé conciso)
- Empieza con un hook directo y llamativo
- Incluye 3-5 hashtags relevantes (mezcla trending y nicho)
- Tono juvenil y dinámico pero no forzado
- Si aplica, incluye un emoji o dos""",
        
        "youtube_title": """Genera SOLO un título para YOUTUBE.
- Máximo 100 caracteres
- Debe ser SEO-friendly (incluye keywords relevantes)
- Usa números si aplica (ej: "5 trucos para...")
- Debe generar curiosidad sin ser clickbait engañoso
- NO incluyas emojis en el título""",
        
        "youtube_description": """Genera una descripción para YOUTUBE.
- 200-500 palabras
- Primer párrafo: resumen atractivo del contenido (esto aparece en búsquedas)
- Incluye timestamps ficticios si el contenido lo amerita (ej: 0:00 Intro, 1:30 Primer tip)
- Incluye call-to-action: suscribirse, dar like, comentar
- Al final: 10-15 tags/keywords separados por comas
- NO incluyas links ficticios""",
    }
    
    base = f"""TEMA: {tema}
{f'DESCRIPCIÓN ADICIONAL: {descripcion}' if descripcion else ''}
TONO: {tono}

{platform_instructions.get(platform, 'Genera texto para una publicación en redes sociales.')}

Responde SOLO con el texto generado. Sin explicaciones ni comentarios adicionales."""
    
    return base


async def generate_text_for_platform(tema: str, descripcion: str | None, tono: str, platform: str) -> str:
    """Genera texto para UNA plataforma específica."""
    if not client:
        raise RuntimeError("Gemini AI no configurado. Agrega GEMINI_API_KEY al .env")
    
    prompt = _build_prompt(tema, descripcion, tono, platform)
    
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.8,  # Creatividad moderada-alta
            max_output_tokens=1024,
        ),
    )
    
    return response.text.strip()


async def generate_all_texts(tema: str, descripcion: str | None = None, tono: str = "profesional") -> dict:
    """Genera texto para TODAS las plataformas."""
    platforms = ["facebook", "instagram", "tiktok", "youtube_title", "youtube_description"]
    
    results = {}
    for platform in platforms:
        try:
            text = await generate_text_for_platform(tema, descripcion, tono, platform)
            results[platform] = text
        except Exception as e:
            results[platform] = f"[Error: {str(e)}]"
    
    # Extraer tags de YouTube del texto generado
    results["youtube_tags"] = _extract_youtube_tags(results.get("youtube_description", ""))
    
    return results


def _extract_youtube_tags(description: str) -> list[str]:
    """Intenta extraer tags del final de la descripción de YouTube."""
    lines = description.strip().split("\n")
    # Buscar la última línea que parezca una lista de tags
    for line in reversed(lines):
        if "," in line and len(line.split(",")) >= 3:
            return [tag.strip() for tag in line.split(",") if tag.strip()]
    return []
```

---

## PASO 10: Crear backend/publishers/base.py

```python
"""
Clase base para todos los publishers de redes sociales.
Cada plataforma hereda de esta clase e implementa sus métodos.
"""

from abc import ABC, abstractmethod


class BasePublisher(ABC):
    """Interfaz común para todos los publishers."""
    
    platform: str = "unknown"
    
    @abstractmethod
    async def publish(self, text: str, media_path: str | None = None, **kwargs) -> dict:
        """
        Publica contenido en la plataforma.
        
        Args:
            text: Texto/caption de la publicación
            media_path: Ruta al archivo de video o imagen (opcional)
            **kwargs: Parámetros adicionales específicos de la plataforma
        
        Returns:
            dict con al menos: {"success": bool, "post_id": str, "url": str}
        """
        pass
    
    @abstractmethod
    async def validate_credentials(self) -> bool:
        """Verifica que las credenciales de la plataforma sean válidas."""
        pass
    
    def get_platform_name(self) -> str:
        """Retorna el nombre de la plataforma."""
        return self.platform
```

---

## PASO 11: Crear backend/main.py

```python
"""
Auto Publisher API — Backend principal con FastAPI.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config import validate_config
from models import GenerateTextRequest, GenerateTextResponse, CreatePostRequest, PostResponse
from services.ai_text import generate_all_texts
from database.posts import crear_post, crear_variante, obtener_post, listar_posts


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ejecuta validaciones al iniciar el servidor."""
    config_ok = validate_config()
    if config_ok:
        print("✅ Configuración válida. Auto Publisher listo.")
    else:
        print("⚠️  Configuración incompleta. Algunas funciones no estarán disponibles.")
    yield
    print("👋 Auto Publisher detenido.")


app = FastAPI(
    title="Auto Publisher API",
    description="API para publicación automatizada en redes sociales con IA",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS para el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, restringir a la URL del frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check."""
    return {"status": "ok", "service": "Auto Publisher API", "version": "1.0.0"}


@app.post("/api/generate-text", response_model=GenerateTextResponse)
async def generate_text(request: GenerateTextRequest):
    """
    Genera texto optimizado para cada red social usando Gemini AI.
    
    Recibe un tema y opcionalmente una descripción y tono.
    Retorna texto adaptado para Facebook, Instagram, TikTok y YouTube.
    """
    try:
        results = await generate_all_texts(
            tema=request.tema,
            descripcion=request.descripcion,
            tono=request.tono,
        )
        return GenerateTextResponse(
            facebook=results.get("facebook", ""),
            instagram=results.get("instagram", ""),
            tiktok=results.get("tiktok", ""),
            youtube_title=results.get("youtube_title", ""),
            youtube_description=results.get("youtube_description", ""),
            youtube_tags=results.get("youtube_tags", []),
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando texto: {str(e)}")


@app.post("/api/posts", response_model=PostResponse)
async def create_post(request: CreatePostRequest):
    """
    Crea un post completo: genera texto para todas las plataformas seleccionadas
    y lo guarda en Supabase.
    """
    try:
        # 1. Generar texto con IA para cada plataforma
        texts = await generate_all_texts(
            tema=request.titulo,
            descripcion=request.descripcion,
            tono=request.tono,
        )
        
        # 2. Crear el post en Supabase
        post = await crear_post(
            user_id="default",  # TODO: reemplazar con auth real
            title=request.titulo,
            content=request.descripcion,
        )
        
        # 3. Crear variantes para cada plataforma seleccionada
        variantes = {}
        for platform in request.plataformas:
            if platform == "youtube":
                text = f"{texts.get('youtube_title', '')}\n\n{texts.get('youtube_description', '')}"
            else:
                text = texts.get(platform, "")
            
            if text:
                await crear_variante(
                    post_id=post["id"],
                    platform=platform,
                    generated_text=text,
                )
                variantes[platform] = text
        
        return PostResponse(
            post_id=post["id"],
            status=post["status"],
            variantes=variantes,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando post: {str(e)}")


@app.get("/api/posts")
async def get_posts(user_id: str = "default", limit: int = 20):
    """Lista los posts más recientes."""
    posts = await listar_posts(user_id=user_id, limit=limit)
    return {"posts": posts}


@app.get("/api/posts/{post_id}")
async def get_post(post_id: str):
    """Obtiene un post por su ID con sus variantes."""
    post = await obtener_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post no encontrado")
    return post


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
```

---

## PASO 12: Crear supabase/migrations/001_auto_publisher.sql

```sql
-- ============================================
-- Auto Publisher — Tablas de Supabase
-- Ejecutar en SQL Editor de Supabase
-- ============================================

-- Cuentas de redes sociales conectadas
CREATE TABLE IF NOT EXISTS social_accounts (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id TEXT NOT NULL,
  platform TEXT NOT NULL CHECK (platform IN ('facebook', 'instagram', 'tiktok', 'youtube')),
  account_name TEXT,
  account_id TEXT,
  access_token TEXT,
  refresh_token TEXT,
  token_expires_at TIMESTAMP WITH TIME ZONE,
  page_id TEXT,
  metadata JSONB,
  connected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(user_id, platform, account_id)
);

-- Posts creados
CREATE TABLE IF NOT EXISTS posts (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id TEXT NOT NULL,
  title TEXT,
  content_original TEXT,
  media_url TEXT,
  media_type TEXT CHECK (media_type IN ('video', 'image', NULL)),
  thumbnail_url TEXT,
  status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'scheduled', 'publishing', 'published', 'failed', 'partial')),
  scheduled_at TIMESTAMP WITH TIME ZONE,
  published_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Variantes de texto por plataforma
CREATE TABLE IF NOT EXISTS post_variants (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  post_id UUID REFERENCES posts(id) ON DELETE CASCADE,
  platform TEXT NOT NULL CHECK (platform IN ('facebook', 'instagram', 'tiktok', 'youtube')),
  generated_text TEXT,
  hashtags TEXT,
  caption TEXT,
  status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'publishing', 'published', 'failed', 'skipped')),
  platform_post_id TEXT,
  platform_url TEXT,
  error_message TEXT,
  published_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Log de publicaciones
CREATE TABLE IF NOT EXISTS publish_log (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  post_id UUID REFERENCES posts(id) ON DELETE CASCADE,
  platform TEXT,
  action TEXT,
  details JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_posts_user ON posts(user_id);
CREATE INDEX IF NOT EXISTS idx_posts_status ON posts(status);
CREATE INDEX IF NOT EXISTS idx_posts_scheduled ON posts(scheduled_at) WHERE status = 'scheduled';
CREATE INDEX IF NOT EXISTS idx_post_variants_post ON post_variants(post_id);
CREATE INDEX IF NOT EXISTS idx_social_accounts_user ON social_accounts(user_id);

-- Realtime
ALTER PUBLICATION supabase_realtime ADD TABLE posts;
ALTER PUBLICATION supabase_realtime ADD TABLE post_variants;

-- Deshabilitar RLS por ahora (habilitar cuando se implemente auth)
ALTER TABLE social_accounts DISABLE ROW LEVEL SECURITY;
ALTER TABLE posts DISABLE ROW LEVEL SECURITY;
ALTER TABLE post_variants DISABLE ROW LEVEL SECURITY;
ALTER TABLE publish_log DISABLE ROW LEVEL SECURITY;
```

---

## PASO 13: Crear README.md

```markdown
# Auto Publisher

Sistema de publicación automatizada en redes sociales con IA.

## Funcionalidades
- Genera texto optimizado para Facebook, Instagram, TikTok y YouTube usando Gemini AI
- Genera miniaturas/imágenes con Nano Banana (próximamente)
- Publica automáticamente en múltiples redes sociales
- Controlable desde dashboard web y bot de Telegram

## Stack
- **Backend:** Python + FastAPI
- **IA:** Google Gemini (texto + imágenes)
- **Base de datos:** Supabase (PostgreSQL)
- **Frontend:** Next.js + Tailwind (próximamente)

## Setup

1. Clona el repositorio
2. Copia `backend/.env.example` a `backend/.env` y llena las variables
3. Ejecuta el SQL de `supabase/migrations/001_auto_publisher.sql` en Supabase
4. Instala dependencias y corre el servidor:

```bash
cd backend
pip install -r requirements.txt
python main.py
```

5. Abre `http://localhost:8000/docs` para ver la documentación interactiva de la API

## Autor
Aldair Murillo Mosquera
```

---

## PASO 14: Verificación

Después de crear todos los archivos:

1. Verifica que la estructura de carpetas sea correcta con `ls -R` o `tree`
2. Verifica que no haya errores de sintaxis: `cd backend && python -c "import main"`
3. NO corras el servidor todavía (necesita el .env con las keys reales)

---

## PASO 15: Commit y Push

```bash
git add -A
git commit -m "feat(autopub): backend base con FastAPI + generación de texto con Gemini AI"
git push origin main
```

---

## RESUMEN DE LO QUE SE CREÓ EN ESTA FASE

| Archivo | Qué hace |
|---------|----------|
| `backend/config.py` | Carga variables de entorno |
| `backend/models.py` | Modelos Pydantic para request/response |
| `backend/main.py` | API FastAPI con endpoints: GET /, POST /api/generate-text, POST /api/posts, GET /api/posts |
| `backend/services/ai_text.py` | Genera texto con Gemini para cada red social con prompts especializados |
| `backend/publishers/base.py` | Clase base abstracta para publishers |
| `backend/database/supabase_client.py` | Cliente Supabase con service_role key |
| `backend/database/posts.py` | CRUD de posts y variantes en Supabase |
| `supabase/migrations/001_auto_publisher.sql` | SQL para crear las 4 tablas del proyecto |
| `README.md` | Documentación del proyecto |
| `.gitignore` | Ignora .env, __pycache__, node_modules, etc. |
