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
