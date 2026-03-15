"""
Auto Publisher API — Backend principal con FastAPI.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config import validate_config
from models import GenerateTextRequest, GenerateTextResponse, CreatePostRequest, PostResponse
from services.ai_text import generate_all_texts
from database.posts import crear_post, crear_variante, obtener_post, listar_posts


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
