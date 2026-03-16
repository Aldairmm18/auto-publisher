"""
Publisher de Facebook usando Playwright (automatización del navegador).
Funciona con cuentas personales y Pages.
"""

import os
import asyncio
from playwright.async_api import async_playwright

PROFILE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "cookies", "chrome_profile_facebook")
)


async def login_facebook():
    """
    Abre el navegador para que el usuario inicie sesion manualmente en Facebook.
    Guarda la sesion en un perfil persistente de Chromium.
    Ejecutar UNA SOLA VEZ.
    """
    async with async_playwright() as p:
        os.makedirs(PROFILE_DIR, exist_ok=True)
        context = await p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
            ignore_default_args=["--enable-automation"],
        )
        page = await context.new_page()
        
        await page.goto("https://www.facebook.com")
        
        print("=" * 50)
        print("FACEBOOK: Inicia sesion manualmente en el navegador.")
        print("Cuando estes logueado y veas tu feed, presiona ENTER aqui.")
        print("=" * 50)
        
        input("Presiona ENTER cuando hayas iniciado sesion...")
        
        print(f"Sesion de Facebook guardada en {PROFILE_DIR}")
        await context.close()


async def publish_to_facebook(text: str, image_path: str = None, video_path: str = None) -> dict:
    """
    Publica un post en Facebook usando un perfil persistente.
    Soporta: texto solo, texto + imagen, texto + video.
    """
    if not os.path.exists(PROFILE_DIR):
        raise RuntimeError("No hay sesion de Facebook. Ejecuta login_facebook() primero.")
    
    async with async_playwright() as p:
        os.makedirs(PROFILE_DIR, exist_ok=True)
        context = await p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            headless=True,
            args=["--disable-blink-features=AutomationControlled"],
            ignore_default_args=["--enable-automation"],
        )
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
            await context.close()


# Para ejecutar el login desde terminal:
if __name__ == "__main__":
    asyncio.run(login_facebook())
