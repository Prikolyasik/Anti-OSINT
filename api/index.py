import os
import sys

# Добавляем backend в PYTHONPATH, чтобы импортировать routers
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from dotenv import load_dotenv
# Загружаем .env из backend/ если существует
load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'backend', '.env'))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

# Добавляем backend/routers в путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend', 'routers'))

from routers.email_check import router as email_router
from routers.fake_data import router as fake_router
from routers.pdf_report import router as pdf_router
from routers.username_check import router as username_router
from routers.exif_cleaner import router as exif_router
from routers.identity_manager import router as identity_router
from routers.password_check import router as password_router
from routers.privacy_score import router as privacy_router

app = FastAPI(title="Digital Alibi API")


class StripApiPrefixMiddleware(BaseHTTPMiddleware):
    """Убирает /api prefix из URL для совместимости с Vercel routes."""

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if path.startswith("/api/") and path != "/api/health":
            # Перезаписываем path, убирая /api
            new_path = path[len("/api"):]
            request.scope["path"] = new_path
            request.scope["raw_path"] = new_path.encode()
        return await call_next(request)


app.add_middleware(StripApiPrefixMiddleware)

# CORS
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if ALLOWED_ORIGINS != ["*"] else ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(email_router)
app.include_router(fake_router)
app.include_router(pdf_router)
app.include_router(username_router)
app.include_router(exif_router)
app.include_router(identity_router)
app.include_router(password_router)
app.include_router(privacy_router)


@app.get("/")
def root():
    return {"message": "Digital Alibi API работает!"}


@app.get("/api/health")
def health():
    return {"status": "ok"}


# --- Vercel serverless entry point ---
handler = app
