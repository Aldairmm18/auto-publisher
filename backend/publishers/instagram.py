"""
Publisher de Instagram usando Playwright (automatización del navegador).
Funciona con cuentas personales.
Publica fotos/imágenes con caption.
"""

import os
import asyncio
from playwright.async_api import async_playwright

PROFILE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "cookies", "chrome_profile_instagram")
)


async def login_instagram():
    """
    Abre el navegador para que el usuario inicie sesion manualmente en Instagram.
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
            viewport={"width": 414, "height": 896},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        )
        page = await context.new_page()
        
        await page.goto("https://www.instagram.com")
        
        print("=" * 50)
        print("INSTAGRAM: Inicia sesion manualmente en el navegador.")
        print("Cuando estes logueado y veas tu feed, presiona ENTER aqui.")
        print("=" * 50)
        
        input("Presiona ENTER cuando hayas iniciado sesion...")
        
        print(f"Sesion de Instagram guardada en {PROFILE_DIR}")
        await context.close()


async def publish_to_instagram(caption: str, image_path: str) -> dict:
    """
    Publica una imagen con caption en Instagram.
    REQUIERE una imagen (Instagram no permite posts solo de texto).
    """
    if not os.path.exists(PROFILE_DIR):
        raise RuntimeError("No hay sesion de Instagram. Ejecuta login_instagram() primero.")
    
    if not image_path or not os.path.exists(image_path):
        raise RuntimeError("Instagram requiere una imagen para publicar.")
    
    async with async_playwright() as p:
        os.makedirs(PROFILE_DIR, exist_ok=True)
        context = await p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            headless=True,
            args=["--disable-blink-features=AutomationControlled"],
            ignore_default_args=["--enable-automation"],
            viewport={"width": 414, "height": 896},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        )
        page = await context.new_page()
        
        try:
            await page.goto("https://www.instagram.com", wait_until="domcontentloaded", timeout=30000)
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
            await context.close()


if __name__ == "__main__":
    asyncio.run(login_instagram())
