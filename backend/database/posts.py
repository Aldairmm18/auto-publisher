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
