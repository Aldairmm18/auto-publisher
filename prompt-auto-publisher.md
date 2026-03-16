# Auto Publisher — Publicación Automatizada en Redes Sociales

## RESUMEN DEL PROYECTO

Sistema de publicación automatizada con IA que permite:
1. Subir un video o imagen
2. La IA genera texto optimizado para cada red social
3. Nano Banana (Gemini) genera una miniatura/imagen llamativa
4. Se publica automáticamente en Facebook, Instagram, TikTok y YouTube
5. Todo controlable desde un dashboard web Y un bot de Telegram

**Autor:** Aldair Murillo Mosquera
**Uso:** Videos editados para un familiar + contenido propio personal
**Contenido:** Videos terminados + imágenes con texto generado por IA

---

## ARQUITECTURA GENERAL

```
┌─────────────────────────────────────────────────────────┐
│                    INTERFACES                            │
│  ┌──────────────┐    ┌──────────────────────────────┐   │
│  │ Bot Telegram  │    │ Dashboard Web (React/Next.js)│   │
│  │ @autopub_bot  │    │ autopublisher.vercel.app     │   │
│  └──────┬───────┘    └──────────────┬───────────────┘   │
│         │                            │                    │
│         ▼                            ▼                    │
│  ┌──────────────────────────────────────────────────┐   │
│  │              BACKEND (Python/FastAPI)              │   │
│  │  - API REST para el dashboard                     │   │
│  │  - Handlers del bot de Telegram                   │   │
│  │  - Cola de publicación (job queue)                │   │
│  └──────────┬────────────┬──────────────────────────┘   │
│             │            │                               │
│    ┌────────▼────┐  ┌───▼──────────┐                    │
│    │ Gemini API  │  │ Nano Banana  │                    │
│    │ (texto IA)  │  │ (imágenes IA)│                    │
│    └─────────────┘  └──────────────┘                    │
│             │                                            │
│    ┌────────▼────────────────────────────────────────┐  │
│    │           PUBLISHERS (APIs de redes)              │  │
│    │  Facebook │ Instagram │ TikTok │ YouTube          │  │
│    └──────────────────────────────────────────────────┘  │
│             │                                            │
│    ┌────────▼────────────────────────────────────────┐  │
│    │              SUPABASE (PostgreSQL)                │  │
│    │  - Posts programados y publicados                 │  │
│    │  - Cuentas de redes conectadas                    │  │
│    │  - Historial de publicaciones                     │  │
│    │  - Storage de archivos (videos/imágenes)          │  │
│    └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## STACK TÉCNICO

### Backend
- **Framework:** Python + FastAPI (API REST + WebSockets)
- **Bot:** python-telegram-bot 22.6 (async)
- **IA texto:** google-genai (Gemini, mismo que el bot de finanzas)
- **IA imágenes:** google-genai con Nano Banana (Gemini imagen)
- **Cola de trabajos:** APScheduler o Celery (para publicaciones programadas)
- **Hosting:** Render (mismo que el bot de finanzas)

### Frontend (Dashboard)
- **Framework:** React + Next.js (o Vite + React si preferimos más simple)
- **UI:** Tailwind CSS
- **Hosting:** Vercel (gratis)
- **Auth:** Supabase Auth (reutilizar el mismo sistema de la app de finanzas)

### Base de Datos
- **Supabase** (mismo proyecto de finanzas: `https://scvltqqtkjazopjyauyv.supabase.co`)
- **Storage:** Supabase Storage para archivos de video/imagen

### APIs de Redes Sociales
- **Facebook:** Graph API v19+ (Pages API)
- **Instagram:** Instagram Graph API (via Meta/Facebook)
- **TikTok:** Content Posting API
- **YouTube:** YouTube Data API v3

---

## ESTRUCTURA DEL PROYECTO

```
auto-publisher/
├── backend/
│   ├── main.py                 # FastAPI app + endpoints REST
│   ├── bot.py                  # Bot de Telegram handlers
│   ├── config.py               # Variables de entorno y configuración
│   ├── models.py               # Modelos Pydantic para request/response
│   │
│   ├── services/
│   │   ├── ai_text.py          # Gemini: genera texto para cada red social
│   │   ├── ai_image.py         # Nano Banana: genera miniaturas/imágenes
│   │   ├── scheduler.py        # Cola de publicación programada
│   │   └── storage.py          # Supabase Storage: subir/descargar archivos
│   │
│   ├── publishers/
│   │   ├── base.py             # Clase base Publisher (interfaz común)
│   │   ├── facebook.py         # Facebook Graph API publisher
│   │   ├── instagram.py        # Instagram Graph API publisher
│   │   ├── tiktok.py           # TikTok Content Posting API publisher
│   │   └── youtube.py          # YouTube Data API publisher
│   │
│   ├── database/
│   │   ├── supabase_client.py  # Cliente Supabase
│   │   ├── posts.py            # CRUD de posts
│   │   └── accounts.py         # CRUD de cuentas de redes conectadas
│   │
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx            # Dashboard principal
│   │   │   ├── create/page.tsx     # Crear nuevo post
│   │   │   ├── history/page.tsx    # Historial de publicaciones
│   │   │   ├── accounts/page.tsx   # Gestionar cuentas de redes
│   │   │   └── settings/page.tsx   # Configuración
│   │   │
│   │   ├── components/
│   │   │   ├── PostEditor.tsx      # Editor de post con preview por red
│   │   │   ├── MediaUploader.tsx   # Subir video/imagen
│   │   │   ├── ThumbnailPreview.tsx # Preview de miniatura generada
│   │   │   ├── NetworkSelector.tsx  # Seleccionar en qué redes publicar
│   │   │   ├── SchedulePicker.tsx   # Programar fecha/hora
│   │   │   └── PostCard.tsx        # Card de post en historial
│   │   │
│   │   └── lib/
│   │       ├── api.ts              # Cliente HTTP para el backend
│   │       └── supabase.ts         # Cliente Supabase
│   │
│   ├── package.json
│   └── tailwind.config.ts
│
├── supabase/
│   └── migrations/
│       └── 001_auto_publisher.sql  # Tablas del proyecto
│
└── README.md
```

---

## TABLAS DE SUPABASE (nuevas, en el mismo proyecto)

```sql
-- Cuentas de redes sociales conectadas
CREATE TABLE social_accounts (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id TEXT NOT NULL,
  platform TEXT NOT NULL CHECK (platform IN ('facebook', 'instagram', 'tiktok', 'youtube')),
  account_name TEXT,
  account_id TEXT,               -- ID de la cuenta en la plataforma
  access_token TEXT,              -- Token de acceso (encriptado idealmente)
  refresh_token TEXT,
  token_expires_at TIMESTAMP WITH TIME ZONE,
  page_id TEXT,                   -- Para Facebook/Instagram (Page ID)
  metadata JSONB,                 -- Info adicional de la cuenta
  connected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(user_id, platform, account_id)
);

-- Posts creados (programados o publicados)
CREATE TABLE posts (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id TEXT NOT NULL,
  title TEXT,
  content_original TEXT,          -- Texto original del usuario
  media_url TEXT,                 -- URL del archivo en Supabase Storage
  media_type TEXT CHECK (media_type IN ('video', 'image')),
  thumbnail_url TEXT,             -- URL de la miniatura generada por IA
  status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'scheduled', 'publishing', 'published', 'failed', 'partial')),
  scheduled_at TIMESTAMP WITH TIME ZONE,
  published_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Texto generado por IA para cada red social
CREATE TABLE post_variants (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  post_id UUID REFERENCES posts(id) ON DELETE CASCADE,
  platform TEXT NOT NULL CHECK (platform IN ('facebook', 'instagram', 'tiktok', 'youtube')),
  generated_text TEXT,            -- Texto generado por Gemini para esta red
  hashtags TEXT,                  -- Hashtags sugeridos
  caption TEXT,                   -- Caption final (editado por el usuario o el generado)
  status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'publishing', 'published', 'failed', 'skipped')),
  platform_post_id TEXT,          -- ID del post en la plataforma después de publicar
  platform_url TEXT,              -- URL del post publicado
  error_message TEXT,
  published_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Historial / log de acciones
CREATE TABLE publish_log (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  post_id UUID REFERENCES posts(id) ON DELETE CASCADE,
  platform TEXT,
  action TEXT,                    -- 'generate_text', 'generate_thumbnail', 'publish', 'schedule', 'error'
  details JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_posts_user ON posts(user_id);
CREATE INDEX idx_posts_status ON posts(status);
CREATE INDEX idx_posts_scheduled ON posts(scheduled_at) WHERE status = 'scheduled';
CREATE INDEX idx_post_variants_post ON post_variants(post_id);
CREATE INDEX idx_social_accounts_user ON social_accounts(user_id);

-- Habilitar Realtime
ALTER PUBLICATION supabase_realtime ADD TABLE posts;
ALTER PUBLICATION supabase_realtime ADD TABLE post_variants;
```

---

## FASES DE IMPLEMENTACIÓN

### FASE 1: Backend Base + Generación de Texto con IA
**Objetivo:** Backend funcional que recibe un tema/descripción y genera texto optimizado para cada red social.

**Tareas:**
1. Crear proyecto `auto-publisher/backend/` con FastAPI
2. Configurar Supabase client
3. Implementar `services/ai_text.py`:
   - Función `generate_social_text(tema, descripcion, platform)` que usa Gemini
   - El prompt debe generar texto adaptado al estilo de cada red:
     - **Facebook:** Texto más largo, narrativo, con emojis moderados, call-to-action
     - **Instagram:** Caption con emojis, hashtags relevantes, máx 2200 chars
     - **TikTok:** Descripción corta y catchy, hashtags trending, máx 300 chars
     - **YouTube:** Título SEO, descripción larga con timestamps, tags
   - Retorna un dict con el texto generado para cada plataforma
4. Endpoint REST: `POST /api/generate-text`
5. Crear tabla de posts en Supabase (ejecutar SQL)
6. Tests básicos

**Commit:** `feat(autopub): backend base + generación de texto con Gemini`

---

### FASE 2: Generación de Miniaturas con Nano Banana
**Objetivo:** Generar miniaturas/imágenes llamativas automáticamente usando Nano Banana (Gemini imagen).

**Tareas:**
1. Implementar `services/ai_image.py`:
   - Función `generate_thumbnail(tema, descripcion, estilo)` que usa Gemini API con capacidad de imagen
   - Estilos predefinidos: "llamativo", "minimalista", "profesional", "divertido"
   - La imagen generada se sube a Supabase Storage
   - Retorna la URL pública de la imagen
2. Endpoint REST: `POST /api/generate-thumbnail`
3. Integrar con el flujo de creación de posts
4. Preview de la miniatura generada antes de publicar

**Nota sobre Nano Banana API:**
- Usar `google.genai` con el modelo `gemini-2.0-flash-exp` o `imagen-3.0-generate-001`
- Ejemplo:
```python
from google import genai
client = genai.Client(api_key=GEMINI_API_KEY)

response = client.models.generate_images(
    model='imagen-3.0-generate-001',
    prompt='Miniatura llamativa para video de YouTube sobre...',
    config=genai.types.GenerateImagesConfig(
        number_of_images=1,
        output_mime_type='image/png',
    )
)
# response.generated_images[0].image.image_bytes
```

**Commit:** `feat(autopub): generación de miniaturas con Nano Banana/Gemini`

---

### FASE 3: Publisher de Facebook + Instagram
**Objetivo:** Publicar automáticamente en Facebook Pages e Instagram Business.

**Tareas:**
1. Implementar `publishers/facebook.py`:
   - Autenticación via Facebook Graph API (Page Access Token)
   - Función `publish_post(page_id, token, text, media_url)`:
     - Si es imagen: `POST /{page-id}/photos`
     - Si es video: `POST /{page-id}/videos`
     - Si es solo texto: `POST /{page-id}/feed`
   - Función `schedule_post(page_id, token, text, media_url, timestamp)`:
     - Usa `published=false` + `scheduled_publish_time`
   
2. Implementar `publishers/instagram.py`:
   - Instagram usa la misma API de Meta (Graph API)
   - Función `publish_to_instagram(ig_user_id, token, text, media_url)`:
     - Paso 1: Crear media container (`POST /{ig-user-id}/media`)
     - Paso 2: Publicar container (`POST /{ig-user-id}/media_publish`)
   - Soportar: imagen individual, carrusel, Reel (video)

3. Endpoint REST: `POST /api/publish`
4. Guardar resultado en `post_variants` con URL del post publicado

**Requisitos previos (el usuario debe hacer):**
- Crear una app en Meta for Developers (https://developers.facebook.com)
- Obtener Page Access Token con permisos: `pages_manage_posts`, `pages_read_engagement`, `instagram_basic`, `instagram_content_publish`
- Conectar la cuenta de Instagram a una Facebook Page

**Commit:** `feat(autopub): publisher Facebook + Instagram via Graph API`

---

### FASE 4: Publisher de YouTube
**Objetivo:** Subir videos a YouTube con título, descripción, tags y miniatura personalizada.

**Tareas:**
1. Implementar `publishers/youtube.py`:
   - Autenticación via YouTube Data API v3 (OAuth 2.0)
   - Función `upload_video(credentials, video_path, title, description, tags, thumbnail_path)`:
     - Subir video con metadata
     - Subir miniatura custom
     - Opciones de privacidad: public, unlisted, private
   - Función `schedule_video(credentials, video_path, title, description, publish_at)`:
     - Subir como private + programar publicación
   
2. Requisitos:
   - Proyecto en Google Cloud Console
   - Habilitar YouTube Data API v3
   - Crear credenciales OAuth 2.0
   - La primera vez requiere autorización manual en el navegador

**Commit:** `feat(autopub): publisher YouTube via Data API v3`

---

### FASE 5: Publisher de TikTok
**Objetivo:** Subir videos a TikTok automáticamente.

**Tareas:**
1. Implementar `publishers/tiktok.py`:
   - Autenticación via TikTok Content Posting API (OAuth 2.0)
   - Función `upload_video(token, video_path, description)`:
     - Inicializar upload: `POST /v2/post/publish/video/init/`
     - Subir video chunks
     - O usar `PULL_FROM_URL` si el video está en Supabase Storage
   - Opción de publicar como borrador para revisión antes de publicar
   
2. Requisitos:
   - Registrar app en TikTok for Developers
   - Obtener aprobación del scope `video.publish` / `video.upload`
   - Pasar auditoría de TikTok para que los videos sean públicos (sin auditoría son privados)

**Nota:** TikTok es la plataforma más restrictiva. Los videos publicados sin auditoría aprobada serán privados. Considerar empezar con Upload to Inbox (borrador).

**Commit:** `feat(autopub): publisher TikTok via Content Posting API`

---

### FASE 6: Bot de Telegram
**Objetivo:** Controlar el Auto Publisher desde Telegram.

**Bot:** `@autopub_bot` (crear nuevo bot con BotFather)

**Comandos:**
| Comando | Descripción |
|---------|-------------|
| `/start` | Bienvenida + instrucciones |
| `/publicar` | Inicia flujo de publicación (pide tema → genera texto → genera miniatura → confirma → publica) |
| `/programar` | Igual que /publicar pero pide fecha/hora |
| `/estado` | Muestra posts pendientes y su estado |
| `/historial` | Últimas 10 publicaciones con links |
| `/cuentas` | Muestra cuentas de redes conectadas |
| `/ayuda` | Lista de comandos |

**Flujo de `/publicar`:**
1. Bot: "¿Sobre qué es el contenido? Mándame una descripción"
2. Usuario: "Video sobre cómo editar videos en Premiere Pro"
3. Bot: "¿Quieres adjuntar un video o imagen? Mándamelo o escribe 'solo texto'"
4. Usuario: [envía video o imagen]
5. Bot: Genera texto para cada red + miniatura → muestra preview
6. Bot: "¿En cuáles redes publico?" [botones: FB / IG / TikTok / YouTube / Todas]
7. Usuario: [selecciona]
8. Bot: "¿Publicar ahora o programar?"
9. Bot: Publica y confirma con links a cada post

**También acepta texto libre:**
- Si el usuario envía un video o imagen sin comando, el bot pregunta si quiere publicarlo

**Commit:** `feat(autopub): bot de Telegram para controlar publicaciones`

---

### FASE 7: Dashboard Web
**Objetivo:** Interfaz web completa para gestionar todo el Auto Publisher.

**Pantallas:**
1. **Dashboard principal:** Posts recientes, estado de publicaciones, métricas rápidas
2. **Crear post:** Editor con preview por red, subir media, generar texto/miniatura, seleccionar redes, programar
3. **Historial:** Lista de todas las publicaciones con filtros por red, estado, fecha
4. **Cuentas:** Conectar/desconectar cuentas de redes sociales (OAuth flow)
5. **Configuración:** Preferencias de IA (estilo de texto, tono), horarios preferidos, etc.

**Stack:**
- Next.js 14+ (App Router)
- Tailwind CSS
- Supabase Auth (login con el mismo sistema de la app de finanzas)
- Supabase Realtime (estado de publicaciones en tiempo real)
- Deploy en Vercel (gratis)

**Commit:** `feat(autopub): dashboard web con Next.js`

---

### FASE 8: Scheduling y Cola de Publicación
**Objetivo:** Publicaciones programadas que se ejecutan automáticamente a la hora indicada.

**Tareas:**
1. Implementar `services/scheduler.py`:
   - Job queue que revisa cada minuto si hay posts programados para publicar
   - Ejecuta la publicación en todas las redes seleccionadas
   - Actualiza estado en Supabase (publishing → published/failed)
   - Reintentos automáticos en caso de error (máx 3 intentos)
2. Integrar con el backend (APScheduler corriendo en background)
3. Notificación por Telegram cuando un post programado se publica o falla

**Commit:** `feat(autopub): scheduler para publicaciones programadas`

---

## VARIABLES DE ENTORNO

```env
# General
SUPABASE_URL=https://scvltqqtkjazopjyauyv.supabase.co
SUPABASE_SERVICE_KEY=<service_role key>
GEMINI_API_KEY=<Google AI API key>

# Telegram
TELEGRAM_BOT_TOKEN=<token del @autopub_bot>

# Facebook / Instagram (Meta)
META_APP_ID=<App ID de Meta for Developers>
META_APP_SECRET=<App Secret>
FACEBOOK_PAGE_ID=<ID de la Facebook Page>
FACEBOOK_PAGE_TOKEN=<Long-lived Page Access Token>
INSTAGRAM_USER_ID=<ID de la cuenta de Instagram Business>

# YouTube
YOUTUBE_CLIENT_ID=<OAuth Client ID de Google Cloud>
YOUTUBE_CLIENT_SECRET=<OAuth Client Secret>

# TikTok
TIKTOK_CLIENT_KEY=<Client Key de TikTok for Developers>
TIKTOK_CLIENT_SECRET=<Client Secret>
```

---

## ORDEN DE EJECUCIÓN SUGERIDO

1. **Fase 1** (Backend + texto IA) — la base de todo
2. **Fase 2** (Miniaturas con Nano Banana) — la magia visual
3. **Fase 3** (Facebook + Instagram) — las más fáciles de conectar (misma API de Meta)
4. **Fase 6** (Bot de Telegram) — para probar el flujo completo rápido
5. **Fase 4** (YouTube) — segunda prioridad
6. **Fase 5** (TikTok) — la más compleja por la auditoría
7. **Fase 7** (Dashboard web) — la interfaz visual completa
8. **Fase 8** (Scheduler) — automatización total

## GIT
- Repo nuevo: `https://github.com/Aldairmm18/auto-publisher.git`
- Commits por fase con formato: `feat(autopub): descripción`
- `.env` siempre en `.gitignore`

## NOTAS
- Todo el texto de la UI en español (Colombia)
- El backend debe funcionar si alguna red social no está configurada (graceful degradation)
- Cada publisher es independiente — si TikTok falla, las demás siguen
- Logs detallados para debugging
- El usuario puede editar el texto generado por IA antes de publicar
