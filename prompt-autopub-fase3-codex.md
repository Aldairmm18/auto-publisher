# Auto Publisher — FASE 3: Publishers con Automatización del Navegador

## CONTEXTO
El proyecto Auto Publisher ya tiene backend en FastAPI con generación de texto (Groq) y generación de imágenes (Pollinations). Ahora vamos a agregar la capacidad de PUBLICAR contenido automáticamente en Facebook, Instagram, TikTok y YouTube usando automatización del navegador con Playwright.

El proyecto está en `C:\Users\Aldair Murillo\auto-publisher\backend\`.

Lee TODO antes de empezar. Ejecuta cada paso en orden.

---

## PASO 1: Agregar dependencias a requirements.txt

Abrir `backend/requirements.txt` y agregar estas líneas al final:

```
playwright==1.52.0
tiktok-uploader==1.2.0
```

---

## PASO 2: Instalar Playwright y los navegadores

Ejecutar en la terminal:
```bash
cd backend
pip install playwright tiktok-uploader
playwright install chromium
```

El último comando descarga el navegador Chromium (~200MB). Es necesario para la automatización.

---

## PASO 3: Crear carpeta para cookies

```bash
mkdir -p cookies
```

Esta carpeta guardará las sesiones/cookies de cada red social. Agregar al `.gitignore` del proyecto raíz:
```
backend/cookies/
```

---

## PASO 4: Crear backend/publishers/facebook.py

Crear archivo `backend/publishers/facebook.py` con este contenido:

```python
"""
Publisher de Facebook usando Playwright (automatización del navegador).
Funciona con cuentas personales y Pages.
"""

import os
import asyncio
from playwright.async_api import async_playwright

COOKIES_FILE = os.path.join(os.path.dirname(__file__), "..", "cookies", "facebook_cookies.json")


async def login_facebook():
    """
    Abre el navegador para que el usuario inicie sesión manualmente en Facebook.
    Guarda las cookies para uso futuro.
    Ejecutar UNA SOLA VEZ.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        await page.goto("https://www.facebook.com")
        
        print("=" * 50)
        print("FACEBOOK: Inicia sesión manualmente en el navegador.")
        print("Cuando estés logueado y veas tu feed, presiona ENTER aquí.")
        print("=" * 50)
        
        input("Presiona ENTER cuando hayas iniciado sesión...")
        
        # Guardar cookies
        cookies = await context.cookies()
        
        import json
        os.makedirs(os.path.dirname(COOKIES_FILE), exist_ok=True)
        with open(COOKIES_FILE, "w") as f:
            json.dump(cookies, f)
        
        print(f"✅ Cookies de Facebook guardadas en {COOKIES_FILE}")
        await browser.close()


async def publish_to_facebook(text: str, image_path: str = None, video_path: str = None) -> dict:
    """
    Publica un post en Facebook usando cookies guardadas.
    Soporta: texto solo, texto + imagen, texto + video.
    """
    import json
    
    if not os.path.exists(COOKIES_FILE):
        raise RuntimeError("No hay sesión de Facebook. Ejecuta login_facebook() primero.")
    
    with open(COOKIES_FILE, "r") as f:
        cookies = json.load(f)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        await context.add_cookies(cookies)
        page = await context.new_page()
        
        try:
            await page.goto("https://www.facebook.com", wait_until="networkidle", timeout=30000)
            
            # Buscar el campo de crear post
            # En Facebook, el campo de "¿Qué estás pensando?" abre el modal de post
            create_post = page.locator('[aria-label="Create a post"], [aria-label="Crear una publicación"], [role="button"]:has-text("What\'s on your mind"), [role="button"]:has-text("¿Qué estás pensando")').first
            await create_post.click(timeout=10000)
            await page.wait_for_timeout(2000)
            
            # Escribir el texto
            text_box = page.locator('[contenteditable="true"][role="textbox"]').first
            await text_box.fill(text)
            await page.wait_for_timeout(1000)
            
            # Subir imagen si se proporcionó
            if image_path and os.path.exists(image_path):
                # Buscar botón de foto/video
                photo_btn = page.locator('[aria-label="Photo/video"], [aria-label="Foto/video"]').first
                await photo_btn.click(timeout=5000)
                await page.wait_for_timeout(1000)
                
                file_input = page.locator('input[type="file"][accept*="image"]').first
                await file_input.set_input_files(image_path)
                await page.wait_for_timeout(3000)
            
            # Subir video si se proporcionó
            if video_path and os.path.exists(video_path):
                photo_btn = page.locator('[aria-label="Photo/video"], [aria-label="Foto/video"]').first
                await photo_btn.click(timeout=5000)
                await page.wait_for_timeout(1000)
                
                file_input = page.locator('input[type="file"][accept*="video"]').first
                await file_input.set_input_files(video_path)
                await page.wait_for_timeout(5000)
            
            # Click en "Publicar" / "Post"
            post_btn = page.locator('[aria-label="Post"], [aria-label="Publicar"]').first
            await post_btn.click(timeout=10000)
            await page.wait_for_timeout(5000)
            
            return {"success": True, "platform": "facebook", "message": "Post publicado en Facebook"}
        
        except Exception as e:
            return {"success": False, "platform": "facebook", "error": str(e)}
        
        finally:
            await browser.close()


# Para ejecutar el login desde terminal:
if __name__ == "__main__":
    asyncio.run(login_facebook())
```

---

## PASO 5: Crear backend/publishers/instagram.py

Crear archivo `backend/publishers/instagram.py` con este contenido:

```python
"""
Publisher de Instagram usando Playwright (automatización del navegador).
Funciona con cuentas personales.
Publica fotos/imágenes con caption.
"""

import os
import asyncio
from playwright.async_api import async_playwright

COOKIES_FILE = os.path.join(os.path.dirname(__file__), "..", "cookies", "instagram_cookies.json")


async def login_instagram():
    """
    Abre el navegador para que el usuario inicie sesión manualmente en Instagram.
    Guarda las cookies para uso futuro.
    Ejecutar UNA SOLA VEZ.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={"width": 414, "height": 896},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
        )
        page = await context.new_page()
        
        await page.goto("https://www.instagram.com")
        
        print("=" * 50)
        print("INSTAGRAM: Inicia sesión manualmente en el navegador.")
        print("Cuando estés logueado y veas tu feed, presiona ENTER aquí.")
        print("=" * 50)
        
        input("Presiona ENTER cuando hayas iniciado sesión...")
        
        cookies = await context.cookies()
        
        import json
        os.makedirs(os.path.dirname(COOKIES_FILE), exist_ok=True)
        with open(COOKIES_FILE, "w") as f:
            json.dump(cookies, f)
        
        print(f"✅ Cookies de Instagram guardadas en {COOKIES_FILE}")
        await browser.close()


async def publish_to_instagram(caption: str, image_path: str) -> dict:
    """
    Publica una imagen con caption en Instagram.
    REQUIERE una imagen (Instagram no permite posts solo de texto).
    """
    import json
    
    if not os.path.exists(COOKIES_FILE):
        raise RuntimeError("No hay sesión de Instagram. Ejecuta login_instagram() primero.")
    
    if not image_path or not os.path.exists(image_path):
        raise RuntimeError("Instagram requiere una imagen para publicar.")
    
    with open(COOKIES_FILE, "r") as f:
        cookies = json.load(f)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 414, "height": 896},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
        )
        await context.add_cookies(cookies)
        page = await context.new_page()
        
        try:
            await page.goto("https://www.instagram.com", wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(3000)
            
            # Click en el botón de crear post (+)
            create_btn = page.locator('[aria-label="New post"], [aria-label="Nueva publicación"], svg[aria-label="New post"]').first
            await create_btn.click(timeout=10000)
            await page.wait_for_timeout(2000)
            
            # Subir imagen
            file_input = page.locator('input[type="file"][accept*="image"]').first
            await file_input.set_input_files(image_path)
            await page.wait_for_timeout(3000)
            
            # Click "Next" / "Siguiente"
            next_btn = page.locator('button:has-text("Next"), button:has-text("Siguiente"), [role="button"]:has-text("Next")').first
            await next_btn.click(timeout=10000)
            await page.wait_for_timeout(2000)
            
            # Click "Next" otra vez (filtros)
            next_btn2 = page.locator('button:has-text("Next"), button:has-text("Siguiente"), [role="button"]:has-text("Next")').first
            await next_btn2.click(timeout=10000)
            await page.wait_for_timeout(2000)
            
            # Escribir caption
            caption_box = page.locator('textarea[aria-label="Write a caption..."], textarea[aria-label="Escribe un pie de foto..."]').first
            await caption_box.fill(caption)
            await page.wait_for_timeout(1000)
            
            # Click "Share" / "Compartir"
            share_btn = page.locator('button:has-text("Share"), button:has-text("Compartir"), [role="button"]:has-text("Share")').first
            await share_btn.click(timeout=10000)
            await page.wait_for_timeout(5000)
            
            return {"success": True, "platform": "instagram", "message": "Post publicado en Instagram"}
        
        except Exception as e:
            return {"success": False, "platform": "instagram", "error": str(e)}
        
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(login_instagram())
```

---

## PASO 6: Crear backend/publishers/tiktok_pub.py

Crear archivo `backend/publishers/tiktok_pub.py` con este contenido:

```python
"""
Publisher de TikTok usando la librería tiktok-uploader.
Usa cookies del navegador para autenticación.
"""

import os
import asyncio

COOKIES_FILE = os.path.join(os.path.dirname(__file__), "..", "cookies", "tiktok_cookies.txt")


async def login_tiktok():
    """
    Instrucciones para obtener cookies de TikTok.
    Requiere instalar la extensión 'Get cookies.txt' en Chrome.
    """
    print("=" * 50)
    print("TIKTOK: Para obtener las cookies necesitas:")
    print("1. Instala la extensión 'Get cookies.txt' en Chrome")
    print("   https://chrome.google.com/webstore/detail/get-cookiestxt-locally")
    print("2. Ve a https://www.tiktok.com e inicia sesión")
    print("3. Click en la extensión → Export → guarda el archivo")
    print(f"4. Copia el archivo a: {COOKIES_FILE}")
    print("=" * 50)


async def publish_to_tiktok(video_path: str, description: str) -> dict:
    """
    Publica un video en TikTok usando tiktok-uploader.
    REQUIERE un video (TikTok no permite posts solo de texto/imagen).
    """
    if not os.path.exists(COOKIES_FILE):
        raise RuntimeError("No hay cookies de TikTok. Sigue las instrucciones de login_tiktok().")
    
    if not video_path or not os.path.exists(video_path):
        raise RuntimeError("TikTok requiere un video para publicar.")
    
    try:
        from tiktok_uploader.upload import TikTokUploader
        
        uploader = TikTokUploader(cookies=COOKIES_FILE)
        uploader.upload_video(
            video_path,
            description=description,
        )
        
        return {"success": True, "platform": "tiktok", "message": "Video publicado en TikTok"}
    
    except Exception as e:
        return {"success": False, "platform": "tiktok", "error": str(e)}


if __name__ == "__main__":
    asyncio.run(login_tiktok())
```

---

## PASO 7: Crear backend/publishers/youtube_pub.py

Crear archivo `backend/publishers/youtube_pub.py` con este contenido:

```python
"""
Publisher de YouTube usando Playwright (automatización del navegador).
Funciona con cuentas personales de Google/YouTube.
"""

import os
import asyncio
from playwright.async_api import async_playwright

COOKIES_FILE = os.path.join(os.path.dirname(__file__), "..", "cookies", "youtube_cookies.json")


async def login_youtube():
    """
    Abre el navegador para que el usuario inicie sesión manualmente en YouTube.
    Guarda las cookies para uso futuro.
    Ejecutar UNA SOLA VEZ.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        await page.goto("https://studio.youtube.com")
        
        print("=" * 50)
        print("YOUTUBE: Inicia sesión manualmente en el navegador.")
        print("Cuando estés logueado en YouTube Studio, presiona ENTER aquí.")
        print("=" * 50)
        
        input("Presiona ENTER cuando hayas iniciado sesión...")
        
        cookies = await context.cookies()
        
        import json
        os.makedirs(os.path.dirname(COOKIES_FILE), exist_ok=True)
        with open(COOKIES_FILE, "w") as f:
            json.dump(cookies, f)
        
        print(f"✅ Cookies de YouTube guardadas en {COOKIES_FILE}")
        await browser.close()


async def publish_to_youtube(
    video_path: str,
    title: str,
    description: str,
    tags: list[str] = None,
    thumbnail_path: str = None,
) -> dict:
    """
    Sube un video a YouTube usando YouTube Studio via Playwright.
    """
    import json
    
    if not os.path.exists(COOKIES_FILE):
        raise RuntimeError("No hay sesión de YouTube. Ejecuta login_youtube() primero.")
    
    if not video_path or not os.path.exists(video_path):
        raise RuntimeError("YouTube requiere un video para publicar.")
    
    with open(COOKIES_FILE, "r") as f:
        cookies = json.load(f)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        await context.add_cookies(cookies)
        page = await context.new_page()
        
        try:
            await page.goto("https://studio.youtube.com", wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(3000)
            
            # Click en el botón de subir (Create → Upload videos)
            create_btn = page.locator('#create-icon, [aria-label="Upload videos"], [aria-label="Subir videos"]').first
            await create_btn.click(timeout=10000)
            await page.wait_for_timeout(2000)
            
            upload_option = page.locator('tp-yt-paper-item:has-text("Upload videos"), tp-yt-paper-item:has-text("Subir videos")').first
            await upload_option.click(timeout=5000)
            await page.wait_for_timeout(2000)
            
            # Subir video
            file_input = page.locator('input[type="file"]').first
            await file_input.set_input_files(video_path)
            await page.wait_for_timeout(5000)
            
            # Llenar título
            title_input = page.locator('#textbox[aria-label*="title"], #textbox[aria-label*="título"]').first
            await title_input.fill("")
            await title_input.fill(title)
            await page.wait_for_timeout(1000)
            
            # Llenar descripción
            desc_input = page.locator('#textbox[aria-label*="description"], #textbox[aria-label*="descripción"]').first
            await desc_input.fill(description)
            await page.wait_for_timeout(1000)
            
            # Subir miniatura si se proporcionó
            if thumbnail_path and os.path.exists(thumbnail_path):
                thumb_btn = page.locator('#still-picker button, [aria-label="Upload thumbnail"], [aria-label="Subir miniatura"]').first
                await thumb_btn.click(timeout=5000)
                thumb_input = page.locator('input[type="file"][accept*="image"]').first
                await thumb_input.set_input_files(thumbnail_path)
                await page.wait_for_timeout(3000)
            
            # Seleccionar "Not made for kids"
            not_kids = page.locator('tp-yt-paper-radio-button[name="NOT_MADE_FOR_KIDS"], tp-yt-paper-radio-button[name="VIDEO_MADE_FOR_KIDS_NOT_MFK"]').first
            await not_kids.click(timeout=5000)
            
            # Click Next 3 veces (Details → Monetization → Checks → Visibility)
            for _ in range(3):
                next_btn = page.locator('#next-button, button:has-text("Next"), button:has-text("Siguiente")').first
                await next_btn.click(timeout=10000)
                await page.wait_for_timeout(2000)
            
            # Seleccionar Public
            public_radio = page.locator('tp-yt-paper-radio-button[name="PUBLIC"]').first
            await public_radio.click(timeout=5000)
            await page.wait_for_timeout(1000)
            
            # Click Publish / Publicar
            publish_btn = page.locator('#done-button, button:has-text("Publish"), button:has-text("Publicar")').first
            await publish_btn.click(timeout=10000)
            await page.wait_for_timeout(5000)
            
            return {"success": True, "platform": "youtube", "message": "Video publicado en YouTube"}
        
        except Exception as e:
            return {"success": False, "platform": "youtube", "error": str(e)}
        
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(login_youtube())
```

---

## PASO 8: Crear backend/publishers/login_all.py

Este script permite iniciar sesión en todas las redes de una vez:

```python
"""
Script para iniciar sesión en todas las redes sociales.
Ejecutar UNA VEZ para guardar las cookies.
Después el Auto Publisher las usa automáticamente.
"""

import asyncio
from facebook import login_facebook
from instagram import login_instagram
from tiktok_pub import login_tiktok
from youtube_pub import login_youtube


async def main():
    print("\n🔐 AUTO PUBLISHER — Configuración de cuentas\n")
    print("Vamos a iniciar sesión en cada red social.")
    print("Solo necesitas hacer esto UNA VEZ.\n")
    
    # Facebook
    print("\n--- 1/4: FACEBOOK ---")
    respuesta = input("¿Configurar Facebook? (s/n): ").strip().lower()
    if respuesta == "s":
        await login_facebook()
    
    # Instagram
    print("\n--- 2/4: INSTAGRAM ---")
    respuesta = input("¿Configurar Instagram? (s/n): ").strip().lower()
    if respuesta == "s":
        await login_instagram()
    
    # TikTok
    print("\n--- 3/4: TIKTOK ---")
    respuesta = input("¿Configurar TikTok? (s/n): ").strip().lower()
    if respuesta == "s":
        await login_tiktok()
    
    # YouTube
    print("\n--- 4/4: YOUTUBE ---")
    respuesta = input("¿Configurar YouTube? (s/n): ").strip().lower()
    if respuesta == "s":
        await login_youtube()
    
    print("\n✅ Configuración completa. Ya puedes usar el Auto Publisher.\n")


if __name__ == "__main__":
    asyncio.run(main())
```

---

## PASO 9: Agregar endpoint de publicación en main.py

Abrir `backend/main.py` y agregar estos imports al inicio:
```python
from publishers.facebook import publish_to_facebook
from publishers.instagram import publish_to_instagram
from publishers.tiktok_pub import publish_to_tiktok
from publishers.youtube_pub import publish_to_youtube
```

Agregar este modelo en `models.py`:
```python
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
```

Importar PublishRequest en main.py y agregar este endpoint:

```python
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
                result = await publish_to_facebook(
                    text=request.texto_facebook,
                    image_path=request.image_path,
                    video_path=request.video_path,
                )
                results.append(result)
            
            elif plataforma == "instagram" and request.texto_instagram and request.image_path:
                result = await publish_to_instagram(
                    caption=request.texto_instagram,
                    image_path=request.image_path,
                )
                results.append(result)
            
            elif plataforma == "tiktok" and request.texto_tiktok and request.video_path:
                result = await publish_to_tiktok(
                    video_path=request.video_path,
                    description=request.texto_tiktok,
                )
                results.append(result)
            
            elif plataforma == "youtube" and request.youtube_title and request.video_path:
                result = await publish_to_youtube(
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
```

---

## PASO 10: Verificar

```bash
cd backend
python -c "from publishers.facebook import publish_to_facebook; print('FB OK')"
python -c "from publishers.instagram import publish_to_instagram; print('IG OK')"
python -c "from publishers.tiktok_pub import publish_to_tiktok; print('TK OK')"
python -c "from publishers.youtube_pub import publish_to_youtube; print('YT OK')"
```

Todos deben imprimir "OK".

---

## PASO 11: Commit y push

```bash
git add -A
git commit -m "feat(autopub): publishers con Playwright para Facebook, Instagram, TikTok y YouTube"
git push origin main
```

---

## CÓMO USAR

### 1. Configurar cuentas (una sola vez):
```bash
cd backend/publishers
python login_all.py
```

Esto abre el navegador para cada red social. Inicias sesión manualmente y las cookies se guardan.

### 2. Publicar:
Usar el endpoint `POST /api/publish` o desde código Python directamente.

---

## RESUMEN

| Archivo | Qué hace |
|---------|----------|
| publishers/facebook.py | Login + publicar en Facebook (texto, imagen, video) |
| publishers/instagram.py | Login + publicar en Instagram (imagen + caption) |
| publishers/tiktok_pub.py | Login + publicar en TikTok (video + descripción) |
| publishers/youtube_pub.py | Login + publicar en YouTube (video + título + descripción + miniatura) |
| publishers/login_all.py | Script para configurar todas las cuentas de una vez |
| main.py | Nuevo endpoint POST /api/publish |
| models.py | Nuevo modelo PublishRequest |
