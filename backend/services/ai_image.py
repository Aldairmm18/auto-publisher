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

# Configuración de reintentos
MAX_RETRIES = 3
RETRY_DELAY = 1


def _build_image_prompt(tema: str, descripcion: str | None, estilo: str) -> str:
    """
    Construye un prompt CORTO (máx 200 caracteres) optimizado para Pollinations AI.
    """

    estilos = {
        "llamativo": "eye-catching, vibrant colors, high contrast, bold, professional YouTube thumbnail",
        "minimalista": "clean, minimal, modern design, subtle colors, white space, professional, elegant",
        "profesional": "corporate, polished, professional colors blue dark gray, business, high quality",
        "divertido": "fun, colorful, playful, bright colors, energetic, lively, cartoon elements",
        "cinematico": "cinematic, dramatic lighting, movie poster style, atmospheric, widescreen",
    }

    estilo_desc = estilos.get(estilo, estilos["llamativo"])

    # Construir prompt CORTO manteniendo bajo 200 caracteres
    # Formato: "tema, estilo-specific, no text"
    plain_tema = tema.split(",")[0][:40]  # Primeras 40 chars del tema
    prompt = f"{plain_tema}, {estilo_desc}, no text, social media thumbnail"

    # Asegurar que no exceda 200 caracteres
    if len(prompt) > 200:
        prompt = prompt[:197] + "..."

    return prompt


async def generate_thumbnail(
    tema: str,
    descripcion: str | None = None,
    estilo: str = "llamativo",
    width: int = 1280,
    height: int = 720,
) -> dict:
    """
    Genera una miniatura/imagen usando Pollinations AI con reintentos automáticos.

    Args:
        tema: Tema principal de la imagen
        descripcion: Descripción adicional (opcional)
        estilo: Estilo visual (llamativo, minimalista, profesional, divertido, cinematico)
        width: Ancho en píxeles (default 1280 para 16:9)
        height: Alto en píxeles (default 720 para 16:9)

    Returns:
        dict con: filename, filepath, url (local), prompt_used
    """
    import asyncio
    
    prompt = _build_image_prompt(tema, descripcion, estilo)

    # Construir URL con parámetros
    encoded_prompt = quote(prompt)
    url = f"{POLLINATIONS_API}/prompt/{encoded_prompt}?width={width}&height={height}&model=flux&nologo=true"

    # Descargar imagen con reintentos
    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                # Si la descarga fue exitosa, guardar la imagen
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
        except Exception as e:
            last_error = str(e)
            if attempt < MAX_RETRIES - 1:
                # Esperar antes de reintentar
                await asyncio.sleep(RETRY_DELAY)
                continue
            else:
                # Último intento falló
                raise RuntimeError(f"Error descargando imagen de Pollinations después de {MAX_RETRIES} intentos: {last_error}")


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
