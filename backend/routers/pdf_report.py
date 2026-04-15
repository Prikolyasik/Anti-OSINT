from fastapi import APIRouter
from fastapi.responses import FileResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import httpx
import datetime
import os
import uuid

router = APIRouter(prefix="/report", tags=["PDF Report"])

# Регистрируем шрифты с кириллицей
pdfmetrics.registerFont(TTFont("DejaVu", "fonts/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DejaVu-Bold", "fonts/DejaVuSans-Bold.ttf"))


class ComprehensiveReportRequest(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    privacy_score: Optional[Dict[str, Any]] = None
    email_breaches: Optional[List[Any]] = None
    username_sites: Optional[List[Any]] = None


# ===================== СУЩЕСТВУЮЩИЙ ENDPOINT =====================

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


# ===================== НОВЫЙ ENDPOINT: КОМПЛЕКСНЫЙ ОТЧЁТ =====================

def _draw_text_page(c, x, y, text, font, size, color):
    """Вспомогательная функция для рисования текста."""
    c.setFont(font, size)
    c.setFillColor(color)
    c.drawString(x, y, text)


def _add_new_page(c, width, height, page_num):
    """Добавляет новую страницу с колонтитулом."""
    c.showPage()
    c.setFont("DejaVu", 8)
    c.setFillColor(colors.gray)
    c.drawString(40, 30, f"Digital Alibi — Отчёт | Страница {page_num}")
    c.drawString(width - 200, 30, f"Сгенерировано: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}")
    c.setLineWidth(0.5)
    c.setStrokeColor(colors.lightgrey)
    c.line(40, 40, width - 40, 40)
    return height - 60


@router.post("/comprehensive")
async def generate_comprehensive_report(data: ComprehensiveReportRequest):
    """
    Генерирует комплексный PDF-отчёт по всем параметрам:
    - Email и утечки
    - Username и найденные сайты
    - Анализ пароля
    - Privacy Score и рекомендации
    """
    # Уникальное имя файла
    report_id = uuid.uuid4().hex[:8]
    filename = f"comprehensive_report_{report_id}.pdf"
    filepath = os.path.join("reports", filename)
    os.makedirs("reports", exist_ok=True)

    c = canvas.Canvas(filepath, pagesize=A4)
    width, height = A4
    y = height - 60  # Начальная позиция по Y

    # ==================== ТИТУЛЬНАЯ СТРАНИЦА ====================
    c.setFillColor(colors.HexColor("#1a1a2e"))
    c.rect(0, 0, width, height, fill=True, stroke=False)

    c.setFillColor(colors.HexColor("#00f0ff"))
    c.setFont("DejaVu-Bold", 32)
    c.drawString(60, height - 180, "DIGITAL ALIBI")

    c.setFillColor(colors.white)
    c.setFont("DejaVu-Bold", 22)
    c.drawString(60, height - 230, "Комплексный отчёт о цифровом следе")

    c.setFont("DejaVu", 14)
    c.setFillColor(colors.HexColor("#8888aa"))
    c.drawString(60, height - 270, f"Дата генерации: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}")

    # Проверяемые данные
    c.setFont("DejaVu", 12)
    c.setFillColor(colors.white)
    items_y = height - 330
    if data.email:
        c.drawString(60, items_y, f"Email: {data.email}")
        items_y -= 25
    if data.username:
        c.drawString(60, items_y, f"Username: {data.username}")
        items_y -= 25
    if data.password:
        c.drawString(60, items_y, "Password: **** (анализ выполнен)")
        items_y -= 25

    # Footer титульной страницы
    c.setFont("DejaVu", 10)
    c.setFillColor(colors.HexColor("#00ff88"))
    c.drawString(60, 100, "Anti-OSINT Instrument")
    c.setFillColor(colors.HexColor("#8888aa"))
    c.drawString(60, 75, "Данный отчёт создан в образовательных целях.")

    c.showPage()

    # ==================== СТРАНИЦА 2: EMAIL ====================
    y = height - 60
    page_num = 2

    if data.email:
        # Заголовок секции
        c.setFillColor(colors.HexColor("#1a1a2e"))
        c.rect(0, height - 80, width, 80, fill=True, stroke=False)
        c.setFillColor(colors.HexColor("#00f0ff"))
        c.setFont("DejaVu-Bold", 20)
        c.drawString(40, height - 45, "1. Анализ Email")

        c.setFillColor(colors.white)
        c.setFont("DejaVu", 12)
        c.drawString(40, height - 70, f"Проверяемый email: {data.email}")

        y = height - 120

        # Данные об утечках
        if data.email_breaches:
            breach_count = len(data.email_breaches)
            risk = "низкий" if breach_count == 0 else "средний" if breach_count < 3 else "высокий"
            risk_colors = {"низкий": "#2ecc71", "средний": "#f39c12", "высокий": "#e74c3c"}

            c.setFillColor(colors.HexColor(risk_colors.get(risk, "#888888")))
            c.setFont("DejaVu-Bold", 16)
            c.drawString(40, y, f"Уровень риска: {risk.upper()}")
            y -= 30

            c.setFillColor(colors.black)
            c.setFont("DejaVu", 13)
            c.drawString(40, y, f"Найдено утечек: {breach_count}")
            y -= 35

            if breach_count > 0:
                c.setFont("DejaVu-Bold", 13)
                c.drawString(40, y, "Затронутые базы данных:")
                y -= 25
                c.setFont("DejaVu", 11)

                for breach in data.email_breaches:
                    if y < 60:
                        y = _add_new_page(c, width, height, page_num)
                        page_num += 1

                    if isinstance(breach, dict):
                        name = breach.get("name", "Неизвестно")
                        date = breach.get("date", "")
                        c.drawString(60, y, f"• {name}")
                        if date:
                            c.setFillColor(colors.gray)
                            c.drawString(350, y, f"(дата: {date})")
                            c.setFillColor(colors.black)
                    else:
                        c.drawString(60, y, f"• {breach}")
                    y -= 22
            else:
                c.setFont("DejaVu", 13)
                c.setFillColor(colors.HexColor("#2ecc71"))
                c.drawString(40, y, "✓ Email не найден ни в одной известной утечке")
        else:
            c.setFont("DejaVu", 12)
            c.setFillColor(colors.gray)
            c.drawString(40, y, "Данные об утечках не предоставлены")

    # ==================== СТРАНИЦА: USERNAME ====================
    if data.username:
        c.showPage()
        page_num += 1
        y = height - 60

        c.setFillColor(colors.HexColor("#1a1a2e"))
        c.rect(0, height - 80, width, 80, fill=True, stroke=False)
        c.setFillColor(colors.HexColor("#00f0ff"))
        c.setFont("DejaVu-Bold", 20)
        c.drawString(40, height - 45, "2. Анализ Username")

        c.setFillColor(colors.white)
        c.setFont("DejaVu", 12)
        c.drawString(40, height - 70, f"Проверяемый никнейм: {data.username}")

        y = height - 120

        if data.username_sites:
            found_sites = [s for s in data.username_sites if s.get("exists", False)]
            not_found_sites = [s for s in data.username_sites if not s.get("exists", False) and not s.get("error")]

            c.setFillColor(colors.black)
            c.setFont("DejaVu-Bold", 14)
            c.drawString(40, y, f"Найдено на {len(found_sites)} из {len(data.username_sites)} платформ")
            y -= 30

            if found_sites:
                c.setFont("DejaVu-Bold", 13)
                c.drawString(40, y, "Обнаруженные аккаунты:")
                y -= 25
                c.setFont("DejaVu", 10)

                for site in found_sites:
                    if y < 60:
                        y = _add_new_page(c, width, height, page_num)
                        page_num += 1

                    site_name = site.get("site", "Неизвестно")
                    site_url = site.get("url", "")
                    c.drawString(60, y, f"• {site_name}")
                    c.setFillColor(colors.HexColor("#0077cc"))
                    c.drawString(250, y, site_url[:60])
                    c.setFillColor(colors.black)
                    y -= 20

            if not_found_sites:
                if y < 100:
                    y = _add_new_page(c, width, height, page_num)
                    page_num += 1
                y -= 10
                c.setFont("DejaVu-Bold", 13)
                c.drawString(40, y, "Аккаунт НЕ найден на:")
                y -= 25
                c.setFont("DejaVu", 10)

                for site in not_found_sites[:15]:  # Ограничиваем 15 сайтами
                    site_name = site.get("site", "Неизвестно")
                    c.drawString(60, y, f"○ {site_name}")
                    y -= 18

                if len(not_found_sites) > 15:
                    c.setFillColor(colors.gray)
                    c.drawString(60, y, f"... и ещё {len(not_found_sites) - 15} платформ")
        else:
            c.setFont("DejaVu", 12)
            c.setFillColor(colors.gray)
            c.drawString(40, y, "Данные о проверке username не предоставлены")

    # ==================== СТРАНИЦА: ПАРОЛЬ ====================
    if data.password:
        c.showPage()
        page_num += 1
        y = height - 60

        c.setFillColor(colors.HexColor("#1a1a2e"))
        c.rect(0, height - 80, width, 80, fill=True, stroke=False)
        c.setFillColor(colors.HexColor("#00f0ff"))
        c.setFont("DejaVu-Bold", 20)
        c.drawString(40, height - 45, "3. Анализ Пароля")

        c.setFillColor(colors.white)
        c.setFont("DejaVu", 12)
        c.drawString(40, height - 70, f"Проверен пароль (длина: {len(data.password)} символов)")

        y = height - 120

        # Оценка надёжности пароля
        c.setFillColor(colors.black)
        c.setFont("DejaVu-Bold", 13)
        c.drawString(40, y, "Критерии оценки:")
        y -= 25

        criteria = []
        if len(data.password) >= 12:
            criteria.append(("✓ Длина пароля: хороший", "зелёный"))
        elif len(data.password) >= 8:
            criteria.append(("△ Длина пароля: средняя", "жёлтый"))
        else:
            criteria.append(("✗ Длина пароля: недостаточная", "красный"))

        if any(c.islower() for c in data.password):
            criteria.append(("✓ Содержит строчные буквы", "зелёный"))
        else:
            criteria.append(("✗ Нет строчных букв", "красный"))

        if any(c.isupper() for c in data.password):
            criteria.append(("✓ Содержит заглавные буквы", "зелёный"))
        else:
            criteria.append(("✗ Нет заглавных букв", "красный"))

        if any(c.isdigit() for c in data.password):
            criteria.append(("✓ Содержит цифры", "зелёный"))
        else:
            criteria.append(("✗ Нет цифр", "красный"))

        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?/~`" for c in data.password):
            criteria.append(("✓ Содержит спецсимволы", "зелёный"))
        else:
            criteria.append(("✗ Нет спецсимволов", "красный"))

        criterion_colors = {"зелёный": "#2ecc71", "жёлтый": "#f39c12", "красный": "#e74c3c"}

        c.setFont("DejaVu", 11)
        for criterion, color_key in criteria:
            c.setFillColor(colors.HexColor(criterion_colors[color_key]))
            c.drawString(60, y, criterion)
            y -= 22

        # Рекомендации по паролю
        y -= 10
        c.setFont("DejaVu-Bold", 13)
        c.setFillColor(colors.black)
        c.drawString(40, y, "Рекомендации по паролю:")
        y -= 25
        c.setFont("DejaVu", 11)
        c.setFillColor(colors.black)

        pwd_recommendations = []
        if len(data.password) < 12:
            pwd_recommendations.append("Увеличьте длину пароля минимум до 12 символов")
        if not any(c.isupper() for c in data.password):
            pwd_recommendations.append("Добавьте заглавные буквы (A-Z)")
        if not any(c.isdigit() for c in data.password):
            pwd_recommendations.append("Добавьте цифры (0-9)")
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?/~`" for c in data.password):
            pwd_recommendations.append("Добавьте спецсимволы (!@#$%...)")
        if len(data.password) < 8:
            pwd_recommendations.append("Пароль слишком короткий! Используйте минимум 8 символов")

        if pwd_recommendations:
            for rec in pwd_recommendations:
                c.drawString(60, y, f"• {rec}")
                y -= 22
        else:
            c.setFillColor(colors.HexColor("#2ecc71"))
            c.drawString(60, y, "✓ Пароль соответствует всем критериям надёжности")
    elif data.privacy_score and data.privacy_score.get("details", {}).get("password"):
        # Если пароль не передан, но есть данные из privacy_score
        pwd_details = data.privacy_score["details"]["password"]
        c.showPage()
        page_num += 1
        y = height - 60

        c.setFillColor(colors.HexColor("#1a1a2e"))
        c.rect(0, height - 80, width, 80, fill=True, stroke=False)
        c.setFillColor(colors.HexColor("#00f0ff"))
        c.setFont("DejaVu-Bold", 20)
        c.drawString(40, height - 45, "3. Анализ Пароля")

        y = height - 120
        c.setFillColor(colors.black)
        c.setFont("DejaVu", 12)
        c.drawString(40, y, f"Длина пароля: {pwd_details.get('password_length', 'N/A')} символов")
        y -= 25
        c.drawString(40, y, f"Найден в утечках: {pwd_details.get('pwned_count', 0)} раз")
    else:
        # Если пароль вообще не проверялся
        c.showPage()
        page_num += 1
        y = height - 60
        c.setFillColor(colors.HexColor("#1a1a2e"))
        c.rect(0, height - 80, width, 80, fill=True, stroke=False)
        c.setFillColor(colors.HexColor("#00f0ff"))
        c.setFont("DejaVu-Bold", 20)
        c.drawString(40, height - 45, "3. Анализ Пароля")
        y = height - 120
        c.setFillColor(colors.gray)
        c.setFont("DejaVu", 12)
        c.drawString(40, y, "Пароль не был предоставлен для анализа")

    # ==================== СТРАНИЦА: PRIVACY SCORE ====================
    if data.privacy_score:
        c.showPage()
        page_num += 1
        y = height - 60

        score = data.privacy_score
        score_val = score.get("score", 0)
        rating = score.get("rating", "неизвестно")
        emoji = score.get("emoji", "❓")

        c.setFillColor(colors.HexColor("#1a1a2e"))
        c.rect(0, height - 80, width, 80, fill=True, stroke=False)
        c.setFillColor(colors.HexColor("#00f0ff"))
        c.setFont("DejaVu-Bold", 20)
        c.drawString(40, height - 45, "4. Общий рейтинг приватности")

        c.setFillColor(colors.white)
        c.setFont("DejaVu-Bold", 14)
        c.drawString(40, height - 70, f"{emoji}  Рейтинг: {score_val} / 100")

        y = height - 120

        # Классификация
        score_colors = {"отлично": "#2ecc71", "хорошо": "#00f0ff", "удовлетворительно": "#f39c12",
                        "плохо": "#ff6b6b", "критично": "#ff006e"}
        color = score_colors.get(rating, "#8888aa")

        c.setFillColor(colors.HexColor(color))
        c.setFont("DejaVu-Bold", 18)
        c.drawString(40, y, f"Оценка: {rating.upper()}")
        y -= 35

        c.setFillColor(colors.black)
        c.setFont("DejaVu", 12)
        c.drawString(40, y, f"Общий штраф: {score.get('total_penalty', 0)} баллов")
        y -= 30

        # Детализация штрафов
        details = score.get("details", {})
        if details:
            c.setFont("DejaVu-Bold", 13)
            c.drawString(40, y, "Детализация по категориям:")
            y -= 25
            c.setFont("DejaVu", 11)

            if "email" in details:
                email_data = details["email"]
                breach_count = email_data.get("breach_count", 0)
                penalty = email_data.get("breach_penalty", 0)
                c.drawString(60, y, f"Email: {breach_count} утечек, штраф: -{penalty}")
                y -= 22

            if "username" in details:
                uname_data = details["username"]
                sites_count = uname_data.get("found_on_sites", 0)
                penalty = uname_data.get("spread_penalty", 0)
                c.drawString(60, y, f"Username: найден на {sites_count} сайтах, штраф: -{penalty}")
                y -= 22

            if "password" in details:
                pwd_data = details["password"]
                pwned = pwd_data.get("pwned_count", 0)
                penalty = pwd_data.get("total_password_penalty", 0)
                c.drawString(60, y, f"Пароль: найден в {pwned} утечках, штраф: -{penalty}")
                y -= 22

        # Рекомендации
        y -= 15
        recommendations = score.get("recommendations", [])
        if recommendations:
            c.setFont("DejaVu-Bold", 13)
            c.drawString(40, y, "Персональные рекомендации:")
            y -= 25
            c.setFont("DejaVu", 11)

            for rec in recommendations:
                if y < 60:
                    y = _add_new_page(c, width, height, page_num)
                    page_num += 1
                c.drawString(60, y, f"• {rec}")
                y -= 22

    # ==================== ЗАКЛЮЧИТЕЛЬНАЯ СТРАНИЦА ====================
    c.showPage()
    page_num += 1
    y = height - 60

    c.setFillColor(colors.HexColor("#1a1a2e"))
    c.rect(0, height - 80, width, 80, fill=True, stroke=False)
    c.setFillColor(colors.HexColor("#00f0ff"))
    c.setFont("DejaVu-Bold", 20)
    c.drawString(40, height - 45, "Общие рекомендации")

    y = height - 120
    c.setFillColor(colors.black)
    c.setFont("DejaVu", 11)

    general_recommendations = [
        "Используйте менеджер паролей (Bitwarden, KeePass, 1Password)",
        "Включите двухфакторную аутентификацию (2FA) на всех критичных сервисах",
        "Используйте разные никнеймы для разных платформ",
        "Рассмотрите использование одноразовых email-адресов для регистрации",
        "Регулярно проверяйте свои email на утечки данных",
        "Очищайте EXIF-метаданные перед публикацией фотографий",
        "Используйте фейковые данные при регистрации на сомнительных сайтах",
        "Не используйте один пароль на нескольких сайтах",
        "Проверяйте приватность своих аккаунтов в настройках соцсетей",
        "Используйте VPN или Tor для анонимного browsing",
    ]

    for rec in general_recommendations:
        if y < 60:
            y = _add_new_page(c, width, height, page_num)
            page_num += 1
        c.drawString(60, y, f"• {rec}")
        y -= 24

    # Footer
    y -= 30
    c.setLineWidth(0.5)
    c.setStrokeColor(colors.lightgrey)
    c.line(40, y, width - 40, y)
    y -= 20
    c.setFont("DejaVu", 9)
    c.setFillColor(colors.gray)
    c.drawString(40, y, "Данный отчёт создан инструментом Digital Alibi (Anti-OSINT).")
    c.drawString(40, y - 15, "Все данные получены из открытых источников и предоставлены исключительно в образовательных целях.")

    c.save()
    return FileResponse(filepath, media_type="application/pdf", filename="digital_alibi_report.pdf")