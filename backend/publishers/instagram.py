"""
Publisher de Instagram usando Playwright (automatización del navegador).
Funciona con cuentas personales.
Publica fotos/imágenes con caption.
"""

import os
import traceback
from playwright.sync_api import sync_playwright

PROFILE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "cookies", "chrome_profile_instagram")
)


def login_instagram():
    """
    Abre el navegador para que el usuario inicie sesion manualmente en Instagram.
    Guarda la sesion en un perfil persistente de Chromium.
    Ejecutar UNA SOLA VEZ.
    """
    with sync_playwright() as p:
        os.makedirs(PROFILE_DIR, exist_ok=True)
        context = p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
            ignore_default_args=["--enable-automation"],
            viewport={"width": 414, "height": 896},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        )
        page = context.new_page()

        page.goto("https://www.instagram.com")

        print("=" * 50)
        print("INSTAGRAM: Inicia sesion manualmente en el navegador.")
        print("Cuando estes logueado y veas tu feed, presiona ENTER aqui.")
        print("=" * 50)

        input("Presiona ENTER cuando hayas iniciado sesion...")

        print(f"Sesion de Instagram guardada en {PROFILE_DIR}")
        context.close()


def publish_to_instagram(caption: str, image_path: str) -> dict:
    """
    Publica una imagen con caption en Instagram.
    REQUIERE una imagen (Instagram no permite posts solo de texto).
    """
    if not os.path.exists(PROFILE_DIR):
        raise RuntimeError("No hay sesion de Instagram. Ejecuta login_instagram() primero.")

    if not image_path or not os.path.exists(image_path):
        raise RuntimeError("Instagram requiere una imagen para publicar.")

    with sync_playwright() as p:
        os.makedirs(PROFILE_DIR, exist_ok=True)
        context = p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            headless=True,
            args=["--disable-blink-features=AutomationControlled"],
            ignore_default_args=["--enable-automation"],
            viewport={"width": 414, "height": 896},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        )
        page = context.new_page()

        try:
            print("[INSTAGRAM] Navegando a instagram.com...")
            page.goto("https://www.instagram.com", wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(3000)

            print("[INSTAGRAM] Buscando botón 'Nueva publicación'...")
            create_btn = page.locator('[aria-label="New post"], [aria-label="Nueva publicación"], svg[aria-label="New post"]').first
            print("[INSTAGRAM] Haciendo click en 'Nueva publicación'...")
            create_btn.click(timeout=10000)
            page.wait_for_timeout(2000)

            print(f"[INSTAGRAM] Seteando imagen en input: {image_path}")
            file_input = page.locator('input[type="file"][accept*="image"]').first
            file_input.set_input_files(image_path)
            page.wait_for_timeout(3000)

            print("[INSTAGRAM] Haciendo click en 'Next' (paso 1)...")
            next_btn = page.locator('button:has-text("Next"), button:has-text("Siguiente"), [role="button"]:has-text("Next")').first
            next_btn.click(timeout=10000)
            page.wait_for_timeout(2000)

            print("[INSTAGRAM] Haciendo click en 'Next' (paso 2 - filtros)...")
            next_btn2 = page.locator('button:has-text("Next"), button:has-text("Siguiente"), [role="button"]:has-text("Next")').first
            next_btn2.click(timeout=10000)
            page.wait_for_timeout(2000)

            print(f"[INSTAGRAM] Escribiendo caption ({len(caption)} chars)...")
            caption_box = page.locator('textarea[aria-label="Write a caption..."], textarea[aria-label="Escribe un pie de foto..."]').first
            caption_box.fill(caption)
            page.wait_for_timeout(1000)

            print("[INSTAGRAM] Haciendo click en 'Share'...")
            share_btn = page.locator('button:has-text("Share"), button:has-text("Compartir"), [role="button"]:has-text("Share")').first
            share_btn.click(timeout=10000)
            page.wait_for_timeout(5000)

            print("[INSTAGRAM] Post publicado exitosamente.")
            return {"success": True, "platform": "instagram", "message": "Post publicado en Instagram"}

        except Exception as e:
            print("[INSTAGRAM] ERROR - tomando screenshot de debug...")
            try:
                page.screenshot(path="cookies/debug_instagram.png")
                print("[INSTAGRAM] Screenshot guardado en cookies/debug_instagram.png")
            except Exception as ss_err:
                print(f"[INSTAGRAM] No se pudo tomar screenshot: {ss_err}")
            traceback.print_exc()
            return {"success": False, "platform": "instagram", "error": str(e)}

        finally:
            context.close()


if __name__ == "__main__":
    login_instagram()
