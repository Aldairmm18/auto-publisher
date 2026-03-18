import asyncio
from pathlib import Path

from main import api_publish
from models import PublishRequest


def build_request() -> PublishRequest:
    base_dir = Path(__file__).resolve().parent
    image_path = str(base_dir / "test_image.jpg")
    video_path = str(base_dir / "test_video.mp4")

    texto = "¡Prueba maestra del Auto Publisher 100% automatizado en segundo plano! 🚀🤖"

    return PublishRequest(
        texto_facebook=texto,
        texto_instagram=texto,
        texto_tiktok=texto,
        youtube_title="Prueba maestra Auto Publisher",
        youtube_description=texto,
        image_path=image_path,
        video_path=video_path,
        plataformas=["facebook", "instagram", "tiktok", "youtube"],
    )


async def main():
    print("[MASTER] Iniciando prueba maestra...")
    request = build_request()
    print("[MASTER] Ejecutando orquestador de publicacion...")

    result = await api_publish(request)

    print("[MASTER] Resultados por red:")
    for item in result.get("results", []):
        platform = item.get("platform")
        ok = item.get("success")
        status = "OK" if ok else "ERROR"
        print(f" - {platform}: {status}")
        if not ok:
            print(f"   error: {item.get('error')}")

    print("[MASTER] Prueba maestra finalizada.")


if __name__ == "__main__":
    asyncio.run(main())
