"""
Auto Publisher API — Backend principal con FastAPI.
"""

import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from config import validate_config
from models import GenerateTextRequest, GenerateTextResponse, CreatePostRequest, PostResponse, GenerateThumbnailRequest, ThumbnailResponse, MultipleThumbnailsRequest, PublishRequest
from services.ai_text import generate_all_texts
from services.ai_image import generate_thumbnail, generate_multiple_thumbnails, IMAGES_DIR
from database.posts import crear_post, crear_variante, obtener_post, listar_posts
from publishers.facebook import publish_to_facebook
from publishers.instagram import publish_to_instagram
from publishers.tiktok_pub import publish_to_tiktok
from publishers.youtube_pub import publish_to_youtube


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

# Servir imágenes generadas como archivos estáticos
app.mount("/images", StaticFiles(directory=IMAGES_DIR), name="images")


@app.get("/")
async def root():
    """Health check."""
    return {"status": "ok", "service": "Auto Publisher API", "version": "1.0.0"}


@app.post("/api/generate-text", response_model=GenerateTextResponse)
async def generate_text(request: GenerateTextRequest):
    """
    Genera texto optimizado para cada red social usando Claude AI.
    
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


@app.post("/api/publish")
async def api_publish(request: PublishRequest):
    """
    Publica contenido en las redes sociales seleccionadas.
    Requiere haber iniciado sesión previamente (cookies guardadas).
    """
    results = []
    
    for plataforma in request.plataformas:
        try:
            if plataforma == "facebook" and request.texto_facebook:
                result = await asyncio.to_thread(
                    publish_to_facebook,
                    text=request.texto_facebook,
                    image_path=request.image_path,
                    video_path=request.video_path,
                )
                results.append(result)

            elif plataforma == "instagram" and request.texto_instagram and request.image_path:
                result = await asyncio.to_thread(
                    publish_to_instagram,
                    caption=request.texto_instagram,
                    image_path=request.image_path,
                )
                results.append(result)

            elif plataforma == "tiktok" and request.texto_tiktok and request.video_path:
                result = await asyncio.to_thread(
                    publish_to_tiktok,
                    video_path=request.video_path,
                    description=request.texto_tiktok,
                )
                results.append(result)

            elif plataforma == "youtube" and request.youtube_title and request.video_path:
                result = await asyncio.to_thread(
                    publish_to_youtube,
                    video_path=request.video_path,
                    title=request.youtube_title,
                    description=request.youtube_description or "",
                    thumbnail_path=request.thumbnail_path,
                )
                results.append(result)
            
            else:
                results.append({
                    "success": False,
                    "platform": plataforma,
                    "error": "Faltan datos requeridos para esta plataforma"
                })
        
        except Exception as e:
            results.append({
                "success": False,
                "platform": plataforma,
                "error": str(e)
            })
    
    return {"results": results}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
