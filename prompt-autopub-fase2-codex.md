# Auto Publisher — FASE 2: Generación de Miniaturas con Together AI (FLUX)

## CONTEXTO
El proyecto Auto Publisher ya tiene un backend en FastAPI que genera texto con Groq. Ahora vamos a agregar generación de imágenes/miniaturas usando Together AI con el modelo FLUX. El proyecto está en `C:\Users\Aldair Murillo\auto-publisher\backend\`.

Lee TODO antes de empezar. Ejecuta cada paso en orden.

---

## PASO 1: Agregar dependencia together a requirements.txt

Abrir `backend/requirements.txt` y agregar esta línea al final:
```
together==1.5.0
```

Si da error de versión al instalar, usar:
```
together
```

---

## PASO 2: Agregar variable TOGETHER_API_KEY a config.py

Abrir `backend/config.py`. Buscar esta línea:
```python
# Groq AI (LLaMA 3.3 70B)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
```

Agregar DEBAJO (no reemplazar, AGREGAR):
```python
# Together AI (FLUX imagen)
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY", "")
```

En la función validate_config, agregar esta validación (NO es crítica, solo warning):
Buscar el cierre de la lista de missing y ANTES del return agregar:
```python
    if not TOGETHER_API_KEY:
        print("⚠️  TOGETHER_API_KEY no configurada. La generación de imágenes no funcionará.")
```

---

## PASO 3: Crear backend/services/ai_image.py

Crear un archivo NUEVO: `backend/services/ai_image.py` con este contenido EXACTO:

```python
"""
Servicio de generación de imágenes/miniaturas con Together AI (FLUX).
Genera miniaturas llamativas para publicaciones en redes sociales.
Together AI es gratis ($25 créditos al registrarse).
"""

import base64
import os
import uuid
from datetime import datetime
from together import Together
from config import TOGETHER_API_KEY

# Inicializar cliente de Together AI
client = None
if TOGETHER_API_KEY:
    client = Together(api_key=TOGETHER_API_KEY)
else:
    print("⚠️  TOGETHER_API_KEY no configurada. La generación de imágenes no funcionará.")

# Carpeta donde se guardan las imágenes generadas
IMAGES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "generated_images")
os.makedirs(IMAGES_DIR, exist_ok=True)


def _build_image_prompt(tema: str, descripcion: str | None, estilo: str) -> str:
    """Construye un prompt optimizado para generación de miniaturas."""

    estilos = {
        "llamativo": "Eye-catching, vibrant colors, bold typography space, high contrast, professional YouTube thumbnail style, dynamic composition, attention-grabbing",
        "minimalista": "Clean, minimal, modern design, subtle colors, elegant typography space, white space, professional and refined",
        "profesional": "Corporate style, polished, clean layout, professional colors (blue, dark gray, white), business-appropriate, high quality",
        "divertido": "Fun, colorful, playful design, cartoon-like elements, bright saturated colors, energetic and lively composition",
        "cinematico": "Cinematic look, dramatic lighting, film grain, widescreen composition, movie poster style, atmospheric and moody",
    }

    estilo_desc = estilos.get(estilo, estilos["llamativo"])

    prompt = f"""A professional social media thumbnail about: {tema}.
{f'Additional context: {descripcion}.' if descripcion else ''}
Style: {estilo_desc}.
The image should be visually striking and suitable for a social media post or YouTube thumbnail.
Do NOT include any text or letters in the image. Only visual elements.
High resolution, 16:9 aspect ratio, photorealistic quality."""

    return prompt


async def generate_thumbnail(
    tema: str,
    descripcion: str | None = None,
    estilo: str = "llamativo",
    width: int = 1280,
    height: int = 720,
) -> dict:
    """
    Genera una miniatura/imagen usando Together AI (FLUX).

    Args:
        tema: Tema principal de la imagen
        descripcion: Descripción adicional (opcional)
        estilo: Estilo visual (llamativo, minimalista, profesional, divertido, cinematico)
        width: Ancho en píxeles (default 1280 para 16:9)
        height: Alto en píxeles (default 720 para 16:9)

    Returns:
        dict con: filename, filepath, url (local), prompt_used
    """
    if not client:
        raise RuntimeError("Together AI no configurado. Agrega TOGETHER_API_KEY al .env")

    prompt = _build_image_prompt(tema, descripcion, estilo)

    # Generar imagen con FLUX
    response = client.images.generate(
        model="black-forest-labs/FLUX.1-schnell-Free",
        prompt=prompt,
        width=width,
        height=height,
        steps=4,
        n=1,
        response_format="b64_json",
    )

    if not response.data or not response.data[0].b64_json:
        raise RuntimeError("Together AI no retornó imagen")

    # Decodificar y guardar la imagen
    image_bytes = base64.b64decode(response.data[0].b64_json)
    filename = f"thumb_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.png"
    filepath = os.path.join(IMAGES_DIR, filename)

    with open(filepath, "wb") as f:
        f.write(image_bytes)

    return {
        "filename": filename,
        "filepath": filepath,
        "url": f"/images/{filename}",
        "prompt_used": prompt,
        "estilo": estilo,
        "width": width,
        "height": height,
    }


async def generate_multiple_thumbnails(
    tema: str,
    descripcion: str | None = None,
    estilos: list[str] | None = None,
) -> list[dict]:
    """
    Genera múltiples miniaturas con diferentes estilos para que el usuario elija.

    Args:
        tema: Tema principal
        descripcion: Descripción adicional
        estilos: Lista de estilos a generar (default: llamativo + profesional)

    Returns:
        Lista de dicts con info de cada imagen generada
    """
    if estilos is None:
        estilos = ["llamativo", "profesional"]

    results = []
    for estilo in estilos:
        try:
            result = await generate_thumbnail(tema, descripcion, estilo)
            results.append(result)
        except Exception as e:
            results.append({"error": str(e), "estilo": estilo})

    return results
```

---

## PASO 4: Agregar modelos Pydantic para imágenes en models.py

Abrir `backend/models.py` y agregar estas clases AL FINAL del archivo (después de las clases existentes):

```python
class GenerateThumbnailRequest(BaseModel):
    """Request para generar una miniatura."""
    tema: str                           # Ej: "Tutorial de edición en Premiere Pro"
    descripcion: Optional[str] = None   # Descripción adicional
    estilo: str = "llamativo"           # llamativo, minimalista, profesional, divertido, cinematico
    width: int = 1280                   # Ancho en px
    height: int = 720                   # Alto en px


class ThumbnailResponse(BaseModel):
    """Response de una miniatura generada."""
    filename: str
    url: str
    prompt_used: str
    estilo: str
    width: int
    height: int


class MultipleThumbnailsRequest(BaseModel):
    """Request para generar múltiples miniaturas."""
    tema: str
    descripcion: Optional[str] = None
    estilos: list[str] = ["llamativo", "profesional"]
```

---

## PASO 5: Agregar endpoints de imágenes en main.py

Abrir `backend/main.py`.

Primero, agregar estos imports al inicio del archivo (junto a los otros imports):
```python
from fastapi.staticfiles import StaticFiles
from services.ai_image import generate_thumbnail, generate_multiple_thumbnails, IMAGES_DIR
from models import GenerateThumbnailRequest, ThumbnailResponse, MultipleThumbnailsRequest
```

Segundo, DESPUÉS de la línea que agrega el middleware de CORS, agregar:
```python
# Servir imágenes generadas como archivos estáticos
app.mount("/images", StaticFiles(directory=IMAGES_DIR), name="images")
```

Tercero, agregar estos 2 endpoints ANTES de la línea `if __name__ == "__main__":`:

```python
@app.post("/api/generate-thumbnail", response_model=ThumbnailResponse)
async def api_generate_thumbnail(request: GenerateThumbnailRequest):
    """
    Genera una miniatura/imagen llamativa usando Together AI (FLUX).
    
    Estilos disponibles: llamativo, minimalista, profesional, divertido, cinematico.
    """
    try:
        result = await generate_thumbnail(
            tema=request.tema,
            descripcion=request.descripcion,
            estilo=request.estilo,
            width=request.width,
            height=request.height,
        )
        return ThumbnailResponse(
            filename=result["filename"],
            url=result["url"],
            prompt_used=result["prompt_used"],
            estilo=result["estilo"],
            width=result["width"],
            height=result["height"],
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando miniatura: {str(e)}")


@app.post("/api/generate-thumbnails")
async def api_generate_multiple_thumbnails(request: MultipleThumbnailsRequest):
    """
    Genera múltiples miniaturas con diferentes estilos para comparar.
    """
    try:
        results = await generate_multiple_thumbnails(
            tema=request.tema,
            descripcion=request.descripcion,
            estilos=request.estilos,
        )
        return {"thumbnails": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando miniaturas: {str(e)}")
```

---

## PASO 6: Actualizar .env.example

Abrir `backend/.env.example` y agregar al final:
```
# Together AI (FLUX imagen - $25 gratis)
TOGETHER_API_KEY=tu_together_api_key_aqui
```

---

## PASO 7: Actualizar .env

Abrir `backend/.env` y agregar al final:
```
# Together AI (FLUX imagen - $25 gratis)
TOGETHER_API_KEY=PEDIR_AL_USUARIO
```

IMPORTANTE: Preguntarle al usuario por su TOGETHER_API_KEY para completar el .env.

---

## PASO 8: Agregar generated_images/ al .gitignore

Abrir `.gitignore` (en la RAÍZ del proyecto) y agregar esta línea:
```
# Imágenes generadas por IA
backend/generated_images/
```

---

## PASO 9: Instalar dependencia

```bash
cd backend
pip install together
```

---

## PASO 10: Verificar sintaxis

```bash
cd backend
python -c "from services.ai_image import generate_thumbnail; print('OK')"
```

Si imprime "OK", todo está bien.

---

## PASO 11: Commit y push

```bash
git add -A
git commit -m "feat(autopub): generación de miniaturas con Together AI (FLUX)"
git push origin main
```

---

## CÓMO PROBAR

Después de completar todos los pasos:

1. Llenar TOGETHER_API_KEY en el .env
2. Reiniciar el servidor: `python main.py`
3. Abrir `http://localhost:8000/docs`
4. Probar el endpoint `POST /api/generate-thumbnail` con:
```json
{
  "tema": "Tutorial de edición de video en Premiere Pro",
  "descripcion": "Los atajos más útiles para editar más rápido",
  "estilo": "llamativo"
}
```
5. La respuesta incluye un `url` — abrir `http://localhost:8000{url}` en el navegador para ver la imagen
6. También probar `POST /api/generate-thumbnails` para generar múltiples estilos a la vez

---

## RESUMEN DE ARCHIVOS

| Archivo | Cambio |
|---------|--------|
| requirements.txt | Agregado `together` |
| config.py | Agregado `TOGETHER_API_KEY` |
| services/ai_image.py | NUEVO — genera imágenes con FLUX via Together AI |
| models.py | Agregados 3 modelos: GenerateThumbnailRequest, ThumbnailResponse, MultipleThumbnailsRequest |
| main.py | Agregados 2 endpoints + servir imágenes estáticas |
| .env.example | Agregado TOGETHER_API_KEY |
| .env | Agregar TOGETHER_API_KEY (pedir al usuario) |
| .gitignore | Agregado generated_images/ |
