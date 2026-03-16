"""
Publisher de TikTok usando la librería tiktok-uploader.
Usa cookies del navegador para autenticación.
"""

import os
import asyncio

COOKIES_FILE = os.path.join(os.path.dirname(__file__), "..", "cookies", "tiktok_cookies.txt")


async def login_tiktok():
    """
    Instrucciones para obtener cookies de TikTok.
    Requiere instalar la extensión 'Get cookies.txt' en Chrome.
    """
    print("=" * 50)
    print("TIKTOK: Para obtener las cookies necesitas:")
    print("1. Instala la extensión 'Get cookies.txt' en Chrome")
    print("   https://chrome.google.com/webstore/detail/get-cookiestxt-locally")
    print("2. Ve a https://www.tiktok.com e inicia sesión")
    print("3. Click en la extensión → Export → guarda el archivo")
    print(f"4. Copia el archivo a: {COOKIES_FILE}")
    print("=" * 50)


async def publish_to_tiktok(video_path: str, description: str) -> dict:
    """
    Publica un video en TikTok usando tiktok-uploader.
    REQUIERE un video (TikTok no permite posts solo de texto/imagen).
    """
    if not os.path.exists(COOKIES_FILE):
        raise RuntimeError("No hay cookies de TikTok. Sigue las instrucciones de login_tiktok().")
    
    if not video_path or not os.path.exists(video_path):
        raise RuntimeError("TikTok requiere un video para publicar.")
    
    try:
        from tiktok_uploader.upload import TikTokUploader
        
        uploader = TikTokUploader(cookies=COOKIES_FILE)
        uploader.upload_video(
            video_path,
            description=description,
        )
        
        return {"success": True, "platform": "tiktok", "message": "Video publicado en TikTok"}
    
    except Exception as e:
        return {"success": False, "platform": "tiktok", "error": str(e)}


if __name__ == "__main__":
    asyncio.run(login_tiktok())
