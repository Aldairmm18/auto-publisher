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
            headless=False, # Mantenlo en False para probar
            args=['--disable-blink-features=AutomationControlled'],
            ignore_default_args=['--enable-automation'],
            viewport={'width': 414, 'height': 896},
            user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15'
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
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
            ignore_default_args=["--enable-automation"],
            viewport={"width": 414, "height": 896},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        )
        page = context.new_page()

        try:
            print("[INSTAGRAM] Navegando a instagram.com...")
            page.goto("https://www.instagram.com", wait_until="domcontentloaded", timeout=30000)
            # Esperar a que cargue la pagina
            # Esperar a que cargue la pagina
            page.wait_for_timeout(5000)

            print("[INSTAGRAM] Buscando coordenadas del boton '+' por su ubicacion visual...")
            # 1. Buscar SVGs que esten fisicamente en la esquina superior derecha (y < 150, x > 250)
            coords_plus = page.evaluate(
                '''() => {
                const svgs = Array.from(document.querySelectorAll('svg'));
                const headerSvgs = svgs.filter(s => {
                    const rect = s.getBoundingClientRect();
                    return rect.y > 0 && rect.y < 150 && rect.x > 250 && rect.width > 10;
                });
                if (headerSvgs.length > 0) {
                    // Ordenarlos de izquierda a derecha. El "+" esta a la izquierda del corazon.
                    headerSvgs.sort((a, b) => a.getBoundingClientRect().x - b.getBoundingClientRect().x);
                    const rect = headerSvgs[0].getBoundingClientRect();
                    return {x: rect.x + rect.width/2, y: rect.y + rect.height/2};
                }
                return null;
            }'''
            )

            if coords_plus:
                page.mouse.click(coords_plus["x"], coords_plus["y"])
                print("[INSTAGRAM] Click fisico en '+' realizado.")
            else:
                raise Exception("No se encontraron SVGs en la esquina superior derecha")

            page.wait_for_timeout(2000)

            print("[INSTAGRAM] Buscando coordenadas de 'Publicación'...")
            # 2. Encontrar coordenadas del boton "Publicación" en el menú
            coords_pub = page.evaluate(
                '''() => {
                const elements = Array.from(document.querySelectorAll('span, div, a'));
                const pubBtn = elements.find(el => {
                    const text = (el.textContent || '').trim().toLowerCase();
                    return text === 'publicación' || text === 'publicacion' || text === 'post';
                });
                if(pubBtn) {
                    const rect = pubBtn.getBoundingClientRect();
                    return {x: rect.x + rect.width/2, y: rect.y + rect.height/2};
                }
                return null;
            }'''
            )

            if not coords_pub:
                raise Exception("No se encontro la opcion 'Publicación'")

            print("[INSTAGRAM] Abriendo modal para seleccionar imagen...")
            # 3. Atrapar el file chooser haciendo clic físico
            with page.expect_file_chooser(timeout=15000) as fc_info:
                page.mouse.click(coords_pub["x"], coords_pub["y"])

            file_chooser = fc_info.value
            print(f"[INSTAGRAM] Seteando imagen en file chooser: {image_path}")
            file_chooser.set_files(image_path)

            page.wait_for_timeout(4000)

            print("[INSTAGRAM] Haciendo click en 'Siguiente' (paso 1)...")
            page.locator(':text("Siguiente"):visible, :text("Next"):visible').first.click(timeout=10000)

            # Esperar a que cargue la pantalla final
            page.wait_for_timeout(3000)

            print("[INSTAGRAM] Escribiendo caption...")
            # El textarea suele ser el único en esta vista
            caption_box = page.locator("textarea").first
            caption_box.fill(caption)

            page.wait_for_timeout(2000)

            print("[INSTAGRAM] Haciendo click en 'Compartir'...")
            page.locator(':text("Compartir"):visible, :text("Share"):visible').first.click(timeout=10000)

            # Esperar a que se procese la publicacion
            page.wait_for_timeout(10000)
            print("[INSTAGRAM] Post publicado exitosamente.")

            return {"success": True, "platform": "instagram", "message": "Post publicado en Instagram"}

        except Exception as e:
            print("[INSTAGRAM] ERROR - tomando screenshot de debug...")
            try:
                page.screenshot(path="cookies/debug_instagram.png")
                print("[INSTAGRAM] Screenshot guardado en cookies/debug_instagram.png")
            except:
                pass
            traceback.print_exc()
            return {"success": False, "platform": "instagram", "error": str(e)}

        finally:
            context.close()


if __name__ == "__main__":
    login_instagram()
