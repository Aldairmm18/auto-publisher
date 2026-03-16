"""
Publisher de TikTok usando Playwright (automatizacion del navegador).
Funciona con cuentas personales.
"""

import os
import traceback
from playwright.sync_api import sync_playwright

PROFILE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "cookies", "chrome_profile_tiktok")
)


def login_tiktok():
    """
    Abre el navegador para que el usuario inicie sesion manualmente en TikTok.
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
        )
        page = context.new_page()

        page.goto("https://www.tiktok.com/login")

        print("=" * 50)
        print("TIKTOK: Inicia sesion manualmente en el navegador.")
        print("Cuando hayas iniciado sesion, presiona ENTER aqui.")
        print("=" * 50)

        input("Presiona ENTER cuando hayas iniciado sesion...")

        print(f"Sesion de TikTok guardada en {PROFILE_DIR}")
        context.close()


def _get_upload_scope(page):
    frame_locator = page.frame_locator('iframe[src*="upload"]')
    try:
        if frame_locator.locator('input[type="file"]').count() > 0:
            return frame_locator
    except Exception:
        pass
    return page


def publish_to_tiktok(video_path: str, description: str) -> dict:
    """
    Publica un video en TikTok usando Playwright.
    REQUIERE un video (TikTok no permite posts solo de texto/imagen).
    """
    if not os.path.exists(PROFILE_DIR):
        raise RuntimeError("No hay sesion de TikTok. Ejecuta login_tiktok() primero.")

    if not video_path or not os.path.exists(video_path):
        raise RuntimeError("TikTok requiere un video para publicar.")

    with sync_playwright() as p:
        os.makedirs(PROFILE_DIR, exist_ok=True)
        context = p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            headless=True,
            args=["--disable-blink-features=AutomationControlled"],
            ignore_default_args=["--enable-automation"],
        )
        page = context.new_page()

        try:
            print("[TIKTOK] Navegando a tiktok.com/upload...")
            page.goto("https://www.tiktok.com/upload", wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(3000)

            print("[TIKTOK] Detectando scope (iframe o página principal)...")
            scope = _get_upload_scope(page)
            print(f"[TIKTOK] Scope detectado: {'iframe' if scope != page else 'página principal'}")

            print(f"[TIKTOK] Seteando video en input: {video_path}")
            file_input = scope.locator('input[type="file"]').first
            file_input.set_input_files(video_path)
            page.wait_for_timeout(5000)

            print("[TIKTOK] Haciendo click en caja de descripción...")
            desc_box = scope.locator('[data-e2e="upload-description"], div[contenteditable="true"]').first
            desc_box.click(timeout=10000)
            print(f"[TIKTOK] Escribiendo descripción ({len(description)} chars)...")
            desc_box.fill(description)
            page.wait_for_timeout(1000)

            print("[TIKTOK] Haciendo click en 'Post/Publicar'...")
            post_btn = scope.locator(
                'button:has-text("Post"), button:has-text("Publish"), button:has-text("Publicar")'
            ).first
            post_btn.click(timeout=10000)
            page.wait_for_timeout(5000)

            print("[TIKTOK] Video publicado exitosamente.")
            return {"success": True, "platform": "tiktok", "message": "Video publicado en TikTok"}

        except Exception as e:
            print("[TIKTOK] ERROR - tomando screenshot de debug...")
            try:
                page.screenshot(path="cookies/debug_tiktok.png")
                print("[TIKTOK] Screenshot guardado en cookies/debug_tiktok.png")
            except Exception as ss_err:
                print(f"[TIKTOK] No se pudo tomar screenshot: {ss_err}")
            traceback.print_exc()
            return {"success": False, "platform": "tiktok", "error": str(e)}

        finally:
            context.close()


if __name__ == "__main__":
    login_tiktok()
