"""
Servicio de generación de texto con Claude AI (Anthropic).
Genera texto optimizado para cada red social.
"""

import anthropic
from config import ANTHROPIC_API_KEY

# Inicializar cliente de Claude
client = None
if ANTHROPIC_API_KEY:
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
else:
    print("⚠️  ANTHROPIC_API_KEY no configurada. La generación de texto no funcionará.")


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
        raise RuntimeError("Claude AI no configurado. Agrega ANTHROPIC_API_KEY al .env")
    
    prompt = _build_prompt(tema, descripcion, tono, platform)
    
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": prompt}
        ],
    )
    
    return message.content[0].text.strip()


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
