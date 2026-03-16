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


class PublishRequest(BaseModel):
    """Request para publicar en redes sociales."""
    texto_facebook: Optional[str] = None
    texto_instagram: Optional[str] = None
    texto_tiktok: Optional[str] = None
    youtube_title: Optional[str] = None
    youtube_description: Optional[str] = None
    image_path: Optional[str] = None
    video_path: Optional[str] = None
    thumbnail_path: Optional[str] = None
    plataformas: list[str] = ["facebook", "instagram", "tiktok", "youtube"]
