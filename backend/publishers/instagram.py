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
