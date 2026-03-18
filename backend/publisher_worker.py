import sys
import argparse
from publishers.facebook import publish_to_facebook
from publishers.instagram import publish_to_instagram
from publishers.youtube_pub import publish_to_youtube
from publishers.tiktok_pub import publish_to_tiktok

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", required=True)
    parser.add_argument("--image", required=True)
    parser.add_argument("--video", required=True)
    parser.add_argument("--platforms", required=True)
    args = parser.parse_args()

    platforms = args.platforms.split(",")
    print(f"[WORKER] Iniciando publicación real en: {platforms}")
    print(f"[WORKER] Texto recibido: {args.text[:30]}...")

    if "facebook" in platforms:
        try: publish_to_facebook(text=args.text, image_path=args.image, video_path=args.video)
        except Exception as e: print(f"Error FB: {e}")

    if "instagram" in platforms:
        try: publish_to_instagram(caption=args.text, image_path=args.image)
        except Exception as e: print(f"Error IG: {e}")

    if "youtube" in platforms:
        try: publish_to_youtube(title="Auto Publisher Post", description=args.text, video_path=args.video)
        except Exception as e: print(f"Error YT: {e}")

    if "tiktok" in platforms:
        try: publish_to_tiktok(description=args.text, video_path=args.video)
        except Exception as e: print(f"Error TT: {e}")

    print("[WORKER] Proceso finalizado.")

if __name__ == "__main__":
    main()
