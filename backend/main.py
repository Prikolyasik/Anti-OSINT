import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.email_check import router as email_router
from routers.fake_data import router as fake_router
from routers.pdf_report import router as pdf_router
from routers.username_check import router as username_router
from routers.exif_cleaner import router as exif_router
from routers.identity_manager import router as identity_router
from routers.password_check import router as password_router
from routers.privacy_score import router as privacy_router

app = FastAPI(title="Digital Alibi API")

# CORS — разрешаем все для разработки, в продакшне ограничьте
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

# --- Vercel serverless entry point ---
def handler(request):
    """Entry point для Vercel serverless functions."""
    from mangum import Mangum
    return Mangum(app)(request)