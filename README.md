# Auto Publisher

Sistema de publicación automatizada en redes sociales con IA.

## Funcionalidades
- Genera texto optimizado para Facebook, Instagram, TikTok y YouTube usando Gemini AI
- Genera miniaturas/imágenes con Nano Banana (próximamente)
- Publica automáticamente en múltiples redes sociales
- Controlable desde dashboard web y bot de Telegram

## Stack
- **Backend:** Python + FastAPI
- **IA:** Google Gemini (texto + imágenes)
- **Base de datos:** Supabase (PostgreSQL)
- **Frontend:** Next.js + Tailwind (próximamente)

## Setup

1. Clona el repositorio
2. Copia `backend/.env.example` a `backend/.env` y llena las variables
3. Ejecuta el SQL de `supabase/migrations/001_auto_publisher.sql` en Supabase
4. Instala dependencias y corre el servidor:

```bash
cd backend
pip install -r requirements.txt
python main.py
```

5. Abre `http://localhost:8000/docs` para ver la documentación interactiva de la API

## Autor
Aldair Murillo Mosquera
