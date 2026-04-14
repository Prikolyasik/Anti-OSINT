from fastapi import APIRouter
from fastapi.responses import FileResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import httpx
import datetime
import os

router = APIRouter(prefix="/report", tags=["PDF Report"])

# Регистрируем шрифты с кириллицей
pdfmetrics.registerFont(TTFont("DejaVu", "fonts/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DejaVu-Bold", "fonts/DejaVuSans-Bold.ttf"))

@router.get("/generate")
async def generate_report(email: str):
    api_key = os.getenv("LEAKCHECK_API_KEY")
    if not api_key:
        return {"error": "LEAKCHECK_API_KEY не настроен"}
    
    # Автоматически получаем данные об утечках
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://leakcheck.io/api/public?key={api_key}&check={email}"
        )
    
    data = response.json()
    sources = data.get("sources", []) if data.get("found") else []
    count = len(sources)
    risk = "низкий" if count == 0 else "средний" if count < 3 else "высокий"

    # Генерируем PDF
    filename = f"report_{email.replace('@','_')}.pdf"
    filepath = f"reports/{filename}"
    os.makedirs("reports", exist_ok=True)

    c = canvas.Canvas(filepath, pagesize=A4)
    width, height = A4

    # Заголовок
    c.setFillColor(colors.HexColor("#1a1a2e"))
    c.rect(0, height-80, width, 80, fill=True, stroke=False)
    c.setFillColor(colors.white)
    c.setFont("DejaVu-Bold", 18)
    c.drawString(40, height-45, "Digital Alibi — Отчёт о цифровом следе")
    c.setFont("DejaVu", 10)
    c.drawString(40, height-68, f"Сгенерировано: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}")

    # Email
    c.setFillColor(colors.black)
    c.setFont("DejaVu-Bold", 13)
    c.drawString(40, height-130, f"Проверяемый email: {email}")

    # Уровень риска
    risk_colors = {"низкий": "#2ecc71", "средний": "#f39c12", "высокий": "#e74c3c"}
    c.setFillColor(colors.HexColor(risk_colors.get(risk, "#888888")))
    c.setFont("DejaVu-Bold", 15)
    c.drawString(40, height-165, f"Уровень риска: {risk.upper()}")

    # Количество утечек
    c.setFillColor(colors.black)
    c.setFont("DejaVu", 12)
    c.drawString(40, height-200, f"Найдено утечек: {count}")

    # Список утечек
    y = height - 235
    if sources:
        c.setFont("DejaVu-Bold", 12)
        c.drawString(40, y, "Затронутые базы данных:")
        y -= 25
        c.setFont("DejaVu", 11)
        for source in sources:
            name = source.get("name", source) if isinstance(source, dict) else source
            c.drawString(60, y, f"• {name}")
            y -= 20
    else:
        c.setFont("DejaVu", 12)
        c.setFillColor(colors.HexColor("#2ecc71"))
        c.drawString(40, y, "✓ Email не найден ни в одной известной утечке")
        c.setFillColor(colors.black)
        y -= 30

    # Рекомендации
    y -= 20
    c.setFont("DejaVu-Bold", 13)
    c.drawString(40, y, "Рекомендации:")
    y -= 25
    tips = [
        "Смените пароль на затронутых сервисах",
        "Включите двухфакторную аутентификацию",
        "Используйте уникальные пароли для каждого сайта",
        "Рассмотрите использование менеджера паролей",
        "Используйте фейковые данные при регистрации на сомнительных сайтах",
    ]
    c.setFont("DejaVu", 11)
    for tip in tips:
        c.drawString(60, y, f"• {tip}")
        y -= 20

    c.save()
    return FileResponse(filepath, media_type="application/pdf", filename=filename)