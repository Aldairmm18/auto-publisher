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
