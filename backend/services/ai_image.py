"""
Servicio de generación de imágenes/miniaturas con Pollinations AI.
Genera miniaturas llamativas para publicaciones en redes sociales.
Pollinations es GRATIS y no requiere API key.
"""

import httpx
import os
import uuid
from datetime import datetime
from urllib.parse import quote

# Carpeta donde se guardan las imágenes generadas
IMAGES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "generated_images")
os.makedirs(IMAGES_DIR, exist_ok=True)

# URL base de Pollinations AI
POLLINATIONS_API = "https://image.pollinations.ai"


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
    Genera una miniatura/imagen usando Pollinations AI.

    Args:
        tema: Tema principal de la imagen
        descripcion: Descripción adicional (opcional)
        estilo: Estilo visual (llamativo, minimalista, profesional, divertido, cinematico)
        width: Ancho en píxeles (default 1280 para 16:9)
        height: Alto en píxeles (default 720 para 16:9)

    Returns:
        dict con: filename, filepath, url (local), prompt_used
    """
    prompt = _build_image_prompt(tema, descripcion, estilo)

    # Construir URL con parámetros
    encoded_prompt = quote(prompt)
    url = f"{POLLINATIONS_API}/prompt/{encoded_prompt}?width={width}&height={height}&model=flux&nologo=true"

    # Descargar imagen
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=60.0)
            response.raise_for_status()
        except Exception as e:
            raise RuntimeError(f"Error descargando imagen de Pollinations: {str(e)}")

    if response.status_code != 200:
        raise RuntimeError(f"Pollinations retornó status {response.status_code}")

    # Guardar imagen
    image_bytes = response.content
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
