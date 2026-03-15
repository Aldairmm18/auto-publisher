"""
Cliente de Supabase para el Auto Publisher.
Usa la service_role key para bypass de RLS.
"""

from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_SERVICE_KEY

supabase: Client | None = None

if SUPABASE_URL and SUPABASE_SERVICE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
else:
    print("⚠️  Supabase no configurado. El backend funcionará sin base de datos.")
