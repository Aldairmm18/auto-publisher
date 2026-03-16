"""
Script para iniciar sesión en todas las redes sociales.
Ejecutar UNA VEZ para guardar el perfil persistente de Chromium.
Despues el Auto Publisher lo reutiliza automaticamente.
"""

import asyncio
from facebook import login_facebook
from instagram import login_instagram
from tiktok_pub import login_tiktok
from youtube_pub import login_youtube


async def main():
    print("\n🔐 AUTO PUBLISHER — Configuración de cuentas\n")
    print("Vamos a iniciar sesion en cada red social.")
    print("Solo necesitas hacer esto UNA VEZ.\n")
    
    # Facebook
    print("\n--- 1/4: FACEBOOK ---")
    respuesta = input("¿Configurar Facebook? (s/n): ").strip().lower()
    if respuesta == "s":
        await login_facebook()
    
    # Instagram
    print("\n--- 2/4: INSTAGRAM ---")
    respuesta = input("¿Configurar Instagram? (s/n): ").strip().lower()
    if respuesta == "s":
        await login_instagram()
    
    # TikTok
    print("\n--- 3/4: TIKTOK ---")
    respuesta = input("¿Configurar TikTok? (s/n): ").strip().lower()
    if respuesta == "s":
        await login_tiktok()
    
    # YouTube
    print("\n--- 4/4: YOUTUBE ---")
    respuesta = input("¿Configurar YouTube? (s/n): ").strip().lower()
    if respuesta == "s":
        await login_youtube()
    
    print("\n✅ Configuración completa. Ya puedes usar el Auto Publisher.\n")


if __name__ == "__main__":
    asyncio.run(main())
