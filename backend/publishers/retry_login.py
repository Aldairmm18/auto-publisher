"""
Script para reiniciar sesión en redes sociales específicas.
Permite reintentar si las cookies no se guardaron correctamente.
"""

import asyncio
import os
import json
from pathlib import Path

# Imports
from facebook import login_facebook
from instagram import login_instagram
from tiktok_pub import login_tiktok
from youtube_pub import login_youtube

COOKIES_DIR = os.path.join(os.path.dirname(__file__), "..", "cookies")


def verificar_cookie(platform: str) -> bool:
    """Verifica si una cookie fue guardada y tiene contenido válido."""
    if platform == "tiktok":
        cookie_file = os.path.join(COOKIES_DIR, "tiktok_cookies.txt")
        if os.path.exists(cookie_file) and os.path.getsize(cookie_file) > 10:
            return True
    else:
        cookie_file = os.path.join(COOKIES_DIR, f"{platform}_cookies.json")
        try:
            if os.path.exists(cookie_file):
                with open(cookie_file, "r") as f:
                    data = json.load(f)
                    if isinstance(data, list) and len(data) > 0:
                        return True
        except:
            pass
    return False


async def main():
    print("\n🔄 VERIFICAR Y REINTENTar SESIONES\n")
    print("Estado actual de las cookies:\n")
    
    plataformas = ["facebook", "instagram", "youtube", "tiktok"]
    verificadas = {}
    
    # Verificar estado actual
    for plat in plataformas:
        estado = "✅ OK" if verificar_cookie(plat) else "❌ Falta"
        verificadas[plat] = verificar_cookie(plat)
        print(f"  {plat.upper():12} {estado}")
    
    print("\n" + "=" * 50)
    print("¿Cuál deseas reintentar?\n")
    print("  f) Facebook")
    print("  i) Instagram")
    print("  y) YouTube")
    print("  t) TikTok")
    print("  a) Todas")
    print("  q) Salir")
    print("=" * 50)
    
    opcion = input("\nOpción (f/i/y/t/a/q): ").strip().lower()
    
    if opcion == "q":
        print("Adiós!\n")
        return
    
    opciones_map = {
        "f": ["facebook"],
        "i": ["instagram"],
        "y": ["youtube"],
        "t": ["tiktok"],
        "a": plataformas,
    }
    
    plataformas_reintentar = opciones_map.get(opcion, [])
    
    if not plataformas_reintentar:
        print("❌ Opción inválida.")
        return
    
    print()
    
    # Reintentar cada plataforma
    for plat in plataformas_reintentar:
        print(f"\n{'=' * 50}")
        print(f"INICIANDO SESIÓN EN {plat.upper()}")
        print(f"{'=' * 50}\n")
        
        try:
            if plat == "facebook":
                await login_facebook()
            elif plat == "instagram":
                await login_instagram()
            elif plat == "youtube":
                await login_youtube()
            elif plat == "tiktok":
                await login_tiktok()
            
            # Verificar si se guardó
            if verificar_cookie(plat):
                print(f"✅ {plat.upper()} verificado correctamente.\n")
            else:
                print(f"⚠️  {plat.upper()} podría no haberse guardado correctamente.\n")
        
        except Exception as e:
            print(f"❌ Error con {plat.upper()}: {str(e)}\n")
    
    print("\n" + "=" * 50)
    print("✅ Proceso completado.")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
