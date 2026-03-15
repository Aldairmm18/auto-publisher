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
