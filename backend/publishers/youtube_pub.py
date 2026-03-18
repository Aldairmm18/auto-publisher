"""
Publisher de YouTube usando Playwright (automatización del navegador).
Funciona con cuentas personales de Google/YouTube.
"""

import os
import traceback
from playwright.sync_api import sync_playwright

PROFILE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "cookies", "chrome_profile_youtube")
)


def login_youtube():
    """
    Abre el navegador para que el usuario inicie sesion manualmente en YouTube.
    Guarda la sesion en un perfil persistente de Chromium.
    Ejecutar UNA SOLA VEZ.
    """
    with sync_playwright() as p:
        os.makedirs(PROFILE_DIR, exist_ok=True)
        context = p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            headless=False,
            args=["--disable-blink-features=AutomationControlled", "--window-position=-32000,-32000"],
            ignore_default_args=["--enable-automation"],
        )
        page = context.new_page()

        page.goto("https://accounts.google.com", wait_until="domcontentloaded", timeout=30000)

        print("=" * 50)
        print("YOUTUBE: Inicia sesion manualmente en el navegador.")
        print("Cuando hayas iniciado sesion en Google, presiona ENTER aqui.")
        print("=" * 50)

        input("Presiona ENTER cuando hayas iniciado sesion...")

        print(f"Sesion de YouTube guardada en {PROFILE_DIR}")
        context.close()


def publish_to_youtube(
    video_path: str,
    title: str,
    description: str,
    tags: list[str] = None,
    thumbnail_path: str = None,
) -> dict:
    """
    Sube un video a YouTube usando YouTube Studio via Playwright.
    """
    if not os.path.exists(PROFILE_DIR):
        raise RuntimeError("No hay sesion de YouTube. Ejecuta login_youtube() primero.")

    if not video_path or not os.path.exists(video_path):
        raise RuntimeError("YouTube requiere un video para publicar.")

    with sync_playwright() as p:
        os.makedirs(PROFILE_DIR, exist_ok=True)
        context = p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            headless=False,
            args=["--disable-blink-features=AutomationControlled", "--window-position=-32000,-32000"],
            ignore_default_args=["--enable-automation"],
        )
        page = context.new_page()

        try:
            # Navegar a YouTube Studio y esperar a que cargue
            page.goto("https://studio.youtube.com", wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(5000)

            print("[YOUTUBE] Haciendo clic en el icono de subir video con JS...")
            # Forzar clic directo usando JavaScript para evitar bloqueos del DOM
            page.evaluate(
                '''() => {
                const uploadIcon = document.querySelector('#upload-icon');
                if(uploadIcon) {
                    uploadIcon.click();
                } else {
                    const createBtn = document.querySelector('#create-icon');
                    if(createBtn) createBtn.click();
                }
            }'''
            )

            # Esperar a que se abra el modal blanco de subida
            page.wait_for_timeout(3000)

            print(f"[YOUTUBE] Seteando video en el input: {video_path}")
            # Inyectamos el video directamente al input oculto
            page.locator('input[type="file"]').first.set_input_files(video_path)

            print("[YOUTUBE] Esperando a que el editor procese el video (10s)...")
            page.wait_for_timeout(10000)

            print(f"[YOUTUBE] Llenando título: {title}")
            title_input = page.locator('#textbox[aria-label*="title"], #textbox[aria-label*="título"]').first
            title_input.fill("")
            title_input.fill(title)
            print("[YOUTUBE] Esperando 1s...")
            page.wait_for_timeout(1000)

            print(f"[YOUTUBE] Llenando descripción ({len(description)} chars)...")
            desc_input = page.locator('#description-textarea #textbox, #textbox[aria-label*="video"], #textbox[aria-label*="Tell viewers"], #textbox[aria-label*="Cuéntales"]').first
            desc_input.fill(description)
            print("[YOUTUBE] Esperando 1s...")
            page.wait_for_timeout(1000)

            if thumbnail_path and os.path.exists(thumbnail_path):
                print(f"[YOUTUBE] Subiendo miniatura: {thumbnail_path}")
                thumb_btn = page.locator('#still-picker button, [aria-label="Upload thumbnail"], [aria-label="Subir miniatura"]').first
                thumb_btn.click(timeout=5000)
                print("[YOUTUBE] Seteando archivo de miniatura...")
                thumb_input = page.locator('input[type="file"][accept*="image"]').first
                thumb_input.set_input_files(thumbnail_path)
                print("[YOUTUBE] Esperando 3s...")
                page.wait_for_timeout(3000)

            print("[YOUTUBE] Seleccionando 'Not made for kids'...")
            not_kids = page.locator('tp-yt-paper-radio-button[name="NOT_MADE_FOR_KIDS"], tp-yt-paper-radio-button[name="VIDEO_MADE_FOR_KIDS_NOT_MFK"]').first
            try:
                not_kids.click(force=True, timeout=5000)
            except:
                pass
            # Inyección JS para asegurar que Polymer registre el cambio
            not_kids.evaluate("node => node.click()")

            print("[YOUTUBE] Esperando a que el script de YouTube habilite el botón Next (3s)...")
            page.wait_for_timeout(3000)

            print("[YOUTUBE] Haciendo click en 'Next' (paso 1/3)...")
            next_btn = page.locator('#next-button, button:has-text("Next"), button:has-text("Siguiente")').first
            try:
                next_btn.click(force=True, timeout=5000)
            except:
                next_btn.evaluate("node => node.click()")

            print("[YOUTUBE] Esperando 2s...")
            page.wait_for_timeout(2000)

            print("[YOUTUBE] Haciendo click en 'Next' (paso 2/3)...")
            try:
                next_btn.click(force=True, timeout=5000)
            except:
                next_btn.evaluate("node => node.click()")

            print("[YOUTUBE] Esperando 2s...")
            page.wait_for_timeout(2000)

            print("[YOUTUBE] Haciendo click en 'Next' (paso 3/3)...")
            try:
                next_btn.click(force=True, timeout=5000)
            except:
                next_btn.evaluate("node => node.click()")

            print("[YOUTUBE] Esperando 2s...")
            page.wait_for_timeout(2000)

            print("[YOUTUBE] Seleccionando visibilidad 'Public'...")
            public_radio = page.locator('tp-yt-paper-radio-button[name="PUBLIC"]').first
            public_radio.click(timeout=5000)
            print("[YOUTUBE] Esperando 1s...")
            page.wait_for_timeout(1000)

            print("[YOUTUBE] Haciendo click en 'Publish'...")
            publish_btn = page.locator('#done-button, button:has-text("Publish"), button:has-text("Publicar")').first
            publish_btn.click(timeout=10000)
            print("[YOUTUBE] Esperando 5s...")
            page.wait_for_timeout(5000)

            print("[YOUTUBE] Video publicado exitosamente.")
            return {"success": True, "platform": "youtube", "message": "Video publicado en YouTube"}

        except Exception as e:
            print("[YOUTUBE] ERROR - tomando screenshot de debug...")
            error_details = traceback.format_exc()
            try:
                page.screenshot(path="cookies/debug_youtube.png")
                print("[YOUTUBE] Screenshot guardado en cookies/debug_youtube.png")
            except Exception as ss_err:
                print(f"[YOUTUBE] No se pudo tomar screenshot: {ss_err}")
            traceback.print_exc()
            return {
                "success": False,
                "platform": "youtube",
                "error": f"{e}\n{error_details}",
            }

        finally:
            context.close()


if __name__ == "__main__":
    login_youtube()
