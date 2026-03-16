# Migrar generación de texto de Gemini a Groq (LLaMA 3.3 70B)

## CONTEXTO
La API de Gemini tiene la cuota agotada. Vamos a reemplazar Gemini por Groq que es gratis y muy rápido. El proyecto está en `C:\Users\Aldair Murillo\auto-publisher\backend\`.

Lee TODO este archivo antes de empezar. Ejecuta cada paso en orden.

---

## PASO 1: Modificar backend/requirements.txt

Abrir el archivo `backend/requirements.txt`. Buscar esta línea:
```
google-genai==1.14.0
```

Reemplazarla por:
```
groq==0.25.0
```

El archivo final debe quedar así:
```
fastapi==0.115.0
uvicorn[standard]==0.30.0
python-dotenv==1.0.1
groq==0.25.0
supabase==2.28.0
python-telegram-bot==22.6
python-multipart==0.0.9
aiofiles==24.1.0
```

---

## PASO 2: Modificar backend/config.py

Abrir el archivo `backend/config.py`.

Buscar estas líneas:
```python
# Gemini AI
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
```

Reemplazarlas por:
```python
# Groq AI (LLaMA 3.3 70B)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
```

Buscar esta línea dentro de la función validate_config:
```python
    if not GEMINI_API_KEY:
        missing.append("GEMINI_API_KEY")
```

Reemplazarla por:
```python
    if not GROQ_API_KEY:
        missing.append("GROQ_API_KEY")
```

---

## PASO 3: Reemplazar COMPLETAMENTE backend/services/ai_text.py

BORRAR todo el contenido del archivo `backend/services/ai_text.py` y escribir este código EXACTO:

```python
"""
Servicio de generación de texto con Groq (LLaMA 3.3 70B).
Genera texto optimizado para cada red social.
Groq es gratis, rápido, y no requiere tarjeta de crédito.
"""

from groq import Groq
from config import GROQ_API_KEY

# Inicializar cliente de Groq
client = None
if GROQ_API_KEY:
    client = Groq(api_key=GROQ_API_KEY)
else:
    print("⚠️  GROQ_API_KEY no configurada. La generación de texto no funcionará.")


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
        raise RuntimeError("Groq AI no configurado. Agrega GROQ_API_KEY al .env")
    
    prompt = _build_prompt(tema, descripcion, tono, platform)
    
    chat_completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.8,
        max_tokens=1024,
    )
    
    return chat_completion.choices[0].message.content.strip()


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
    for line in reversed(lines):
        if "," in line and len(line.split(",")) >= 3:
            return [tag.strip() for tag in line.split(",") if tag.strip()]
    return []
```

---

## PASO 4: Modificar backend/.env.example

Abrir `backend/.env.example`. Buscar estas líneas:
```
# Google AI (Gemini)
GEMINI_API_KEY=tu_gemini_api_key_aqui
```

Reemplazarlas por:
```
# Groq AI (LLaMA 3.3 70B - gratis)
GROQ_API_KEY=tu_groq_api_key_aqui
```

---

## PASO 5: Modificar backend/.env

Abrir `backend/.env`. Buscar estas líneas:
```
# Google AI (Gemini)
GEMINI_API_KEY=AIzaSyCFKWh1lmei3VUO_L6q1ofZM8p9MFvbzFw
```

Reemplazarlas por:
```
# Groq AI (LLaMA 3.3 70B - gratis)
GROQ_API_KEY=PEDIR_AL_USUARIO
```

IMPORTANTE: Después de hacer el cambio, preguntarle al usuario por su GROQ_API_KEY para completar el .env.

---

## PASO 6: Instalar nueva dependencia

Ejecutar en la terminal:
```bash
cd backend
pip install groq==0.25.0
```

Si da error de versión, intentar:
```bash
pip install groq
```

---

## PASO 7: Verificar que no queden referencias a Gemini

Buscar en TODOS los archivos de `backend/` si queda alguna referencia a "gemini", "genai", "GEMINI", o "google.genai". Si encuentras alguna, eliminarla o reemplazarla.

Archivos a revisar:
- backend/config.py → debe tener GROQ_API_KEY, NO GEMINI_API_KEY
- backend/services/ai_text.py → debe importar de groq, NO de google.genai
- backend/main.py → NO debería tener referencias directas, pero verificar
- backend/.env.example → debe tener GROQ_API_KEY
- backend/.env → debe tener GROQ_API_KEY

---

## PASO 8: Verificar sintaxis

Ejecutar:
```bash
cd backend
python -c "from services.ai_text import generate_all_texts; print('OK')"
```

Si imprime "OK", todo está bien. Si da error, corregirlo.

---

## PASO 9: Commit y push

```bash
git add -A
git commit -m "refactor(ai): migrar generación de texto de Gemini a Groq (LLaMA 3.3 70B gratis)"
git push origin main
```

---

## RESUMEN DE CAMBIOS

| Archivo | Cambio |
|---------|--------|
| requirements.txt | `google-genai` → `groq` |
| config.py | `GEMINI_API_KEY` → `GROQ_API_KEY` |
| services/ai_text.py | Reescrito completo: usa `groq.Groq` + modelo `llama-3.3-70b-versatile` |
| .env.example | Variable cambiada a `GROQ_API_KEY` |
| .env | Variable cambiada (pedir key al usuario) |
