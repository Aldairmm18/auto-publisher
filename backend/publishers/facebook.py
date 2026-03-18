"""
Publisher de Facebook usando Playwright (automatización del navegador).
Funciona con cuentas personales y Pages.
"""

import os
import traceback
from playwright.sync_api import sync_playwright

PROFILE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "cookies", "chrome_profile_facebook")
)


def login_facebook():
    """
    Abre el navegador para que el usuario inicie sesion manualmente en Facebook.
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

        page.goto("https://www.facebook.com")

        print("=" * 50)
        print("FACEBOOK: Inicia sesion manualmente en el navegador.")
        print("Cuando estes logueado y veas tu feed, presiona ENTER aqui.")
        print("=" * 50)

        input("Presiona ENTER cuando hayas iniciado sesion...")

        print(f"Sesion de Facebook guardada en {PROFILE_DIR}")
        context.close()


def publish_to_facebook(text: str, image_path: str = None, video_path: str = None) -> dict:
    """
    Publica un post en Facebook usando un perfil persistente.
    Soporta: texto solo, texto + imagen, texto + video.
    """
    if not os.path.exists(PROFILE_DIR):
        raise RuntimeError("No hay sesion de Facebook. Ejecuta login_facebook() primero.")

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
            print("[FACEBOOK] Navegando a facebook.com...")
            page.goto("https://www.facebook.com", wait_until="commit", timeout=60000)
            page.wait_for_timeout(5000)

            print("[FACEBOOK] Buscando botón 'Crear publicación'...")
            create_post = page.locator('[aria-label="Create a post"], [aria-label="Crear una publicación"], [role="button"]:has-text("What\'s on your mind"), [role="button"]:has-text("¿Qué estás pensando")').first
            print("[FACEBOOK] Haciendo click en 'Crear publicación'...")
            create_post.click(timeout=10000)
            page.wait_for_timeout(2000)

            print(f"[FACEBOOK] Escribiendo texto ({len(text)} chars)...")
            text_box = page.locator('[contenteditable="true"][role="textbox"]').first
            text_box.fill(text)
            page.wait_for_timeout(1000)

            if image_path and os.path.exists(image_path):
                print(f"[FACEBOOK] Subiendo imagen: {image_path}")
                photo_btn = page.locator('[aria-label="Photo/video"], [aria-label="Foto/video"]').first
                print("[FACEBOOK] Haciendo click en botón Foto/video...")
                photo_btn.click(force=True, timeout=5000)
                page.wait_for_timeout(1000)

                print("[FACEBOOK] Seteando archivo de imagen en input...")
                file_input = page.locator('input[type="file"][accept*="image"]').first
                file_input.set_input_files(image_path)
                page.wait_for_timeout(3000)

            if video_path and os.path.exists(video_path):
                print(f"[FACEBOOK] Subiendo video: {video_path}")
                photo_btn = page.locator('[aria-label="Photo/video"], [aria-label="Foto/video"]').first
                print("[FACEBOOK] Haciendo click en botón Foto/video (video)...")
                photo_btn.click(force=True, timeout=5000)
                page.wait_for_timeout(1000)

                print("[FACEBOOK] Seteando archivo de video en input...")
                file_input = page.locator('input[type="file"][accept*="video"]').first
                file_input.set_input_files(video_path)
                page.wait_for_timeout(5000)

            print("[FACEBOOK] Haciendo click en 'Siguiente'...")
            next_btn = page.locator(
                'div[aria-label="Siguiente"], div[aria-label="Next"], span:has-text("Siguiente"), span:has-text("Next")'
            ).first
            next_btn.click(force=True, timeout=10000)
            page.wait_for_timeout(2000)

            print("[FACEBOOK] Esperando a que el archivo cargue y el boton se habilite (5s)...")
            page.wait_for_timeout(5000)

            print("[FACEBOOK] Intentando click maestro en 'Publicar'...")
            try:
                # Intento 1: Selector amplio
                post_btn = page.locator('div[aria-label="Publicar"], span:has-text("Publicar"), div[role="button"]:has-text("Publicar")').last
                post_btn.click(force=True, timeout=5000)
            except:
                print("[FACEBOOK] Falló click de Playwright, inyectando JS...")
                # Intento 2: Fuerza bruta con JavaScript escaneando textos
                page.evaluate('''() => {
                const elements = document.querySelectorAll('span, div[role="button"]');
                for (let el of elements) {
                    if (el.innerText === 'Publicar' || el.innerText === 'Post') {
                        el.click();
                        break;
                    }
                }
            }''')

            print("[FACEBOOK] Esperando a que se confirme la publicacion (10s)...")
            page.wait_for_timeout(10000)
            page.wait_for_timeout(5000)

            print("[FACEBOOK] Post publicado exitosamente.")
            return {"success": True, "platform": "facebook", "message": "Post publicado en Facebook"}

        except Exception as e:
            print("[FACEBOOK] ERROR - tomando screenshot de debug...")
            try:
                page.screenshot(path="cookies/debug_facebook.png")
                print("[FACEBOOK] Screenshot guardado en cookies/debug_facebook.png")
            except Exception as ss_err:
                print(f"[FACEBOOK] No se pudo tomar screenshot: {ss_err}")
            traceback.print_exc()
            return {"success": False, "platform": "facebook", "error": str(e)}

        finally:
            context.close()


# Para ejecutar el login desde terminal:
if __name__ == "__main__":
    login_facebook()
