"""
Publisher de TikTok usando Playwright (automatizacion del navegador).
Funciona con cuentas personales.
"""

import os
import asyncio
from playwright.async_api import async_playwright

PROFILE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "cookies", "chrome_profile_tiktok")
)


async def login_tiktok():
    """
    Abre el navegador para que el usuario inicie sesion manualmente en TikTok.
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

        await page.goto("https://www.tiktok.com/login")

        print("=" * 50)
        print("TIKTOK: Inicia sesion manualmente en el navegador.")
        print("Cuando hayas iniciado sesion, presiona ENTER aqui.")
        print("=" * 50)

        input("Presiona ENTER cuando hayas iniciado sesion...")

        print(f"Sesion de TikTok guardada en {PROFILE_DIR}")
        await context.close()


async def _get_upload_scope(page):
    frame_locator = page.frame_locator('iframe[src*="upload"]')
    try:
        if await frame_locator.locator('input[type="file"]').count() > 0:
            return frame_locator
    except Exception:
        pass
    return page


async def publish_to_tiktok(video_path: str, description: str) -> dict:
    """
    Publica un video en TikTok usando Playwright.
    REQUIERE un video (TikTok no permite posts solo de texto/imagen).
    """
    if not os.path.exists(PROFILE_DIR):
        raise RuntimeError("No hay sesion de TikTok. Ejecuta login_tiktok() primero.")

    if not video_path or not os.path.exists(video_path):
        raise RuntimeError("TikTok requiere un video para publicar.")

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
            await page.goto("https://www.tiktok.com/upload", wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(3000)

            scope = await _get_upload_scope(page)

            file_input = scope.locator('input[type="file"]').first
            await file_input.set_input_files(video_path)
            await page.wait_for_timeout(5000)

            desc_box = scope.locator('[data-e2e="upload-description"], div[contenteditable="true"]').first
            await desc_box.click(timeout=10000)
            await desc_box.fill(description)
            await page.wait_for_timeout(1000)

            post_btn = scope.locator(
                'button:has-text("Post"), button:has-text("Publish"), button:has-text("Publicar")'
            ).first
            await post_btn.click(timeout=10000)
            await page.wait_for_timeout(5000)

            return {"success": True, "platform": "tiktok", "message": "Video publicado en TikTok"}

        except Exception as e:
            return {"success": False, "platform": "tiktok", "error": str(e)}

        finally:
            await context.close()


if __name__ == "__main__":
    asyncio.run(login_tiktok())
