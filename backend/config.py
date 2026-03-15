"""
Configuración central del Auto Publisher.
Carga variables de entorno desde .env
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")

# Groq AI (LLaMA 3.3 70B)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# Together AI (FLUX imagen)
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY", "")

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# Validación
def validate_config():
    """Verifica que las variables críticas estén presentes."""
    missing = []
    if not SUPABASE_URL:
        missing.append("SUPABASE_URL")
    if not SUPABASE_SERVICE_KEY:
        missing.append("SUPABASE_SERVICE_KEY")
    if not GROQ_API_KEY:
        missing.append("GROQ_API_KEY")
    if not TOGETHER_API_KEY:
        print("⚠️  TOGETHER_API_KEY no configurada. La generación de imágenes no funcionará.")
    if missing:
        print(f"⚠️  Variables faltantes: {', '.join(missing)}")
        print("   Copia .env.example a .env y llena los valores.")
    return len(missing) == 0
