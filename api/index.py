import os
import re
import hashlib
from datetime import datetime
from typing import Optional, List
from contextlib import contextmanager

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel
from mangum import Mangum
from faker import Faker
import httpx
from PIL import Image
from PIL.ExifTags import TAGS
import io

# --- DATABASE (PostgreSQL - Neon) ---

DATABASE_URL = os.environ.get("DATABASE_URL")

_db_initialized = False

def get_db_connection():
    import psycopg2
    from psycopg2.extras import RealDictCursor
    conn = psycopg2.connect(DATABASE_URL)
    return conn, RealDictCursor

def init_db():
    global _db_initialized
    if _db_initialized or not DATABASE_URL:
        return
    try:
        conn, _ = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS identities (
                id SERIAL PRIMARY KEY,
                label TEXT NOT NULL,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT,
                birthdate TEXT,
                address TEXT,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                password_strength TEXT,
                created_at TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()
        _db_initialized = True
    except Exception:
        pass

# --- APP ---

app = FastAPI(title="Digital Alibi API")


class StripApiPrefixMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if path.startswith("/api/") and path != "/api/health":
            new_path = path[len("/api"):]
            request.scope["path"] = new_path
            request.scope["raw_path"] = new_path.encode()
        return await call_next(request)


app.add_middleware(StripApiPrefixMiddleware)

ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if ALLOWED_ORIGINS != ["*"] else ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

fake = Faker("ru_RU")

# --- ROOT ---

@app.get("/")
def root():
    return {"message": "Digital Alibi API работает!"}


@app.get("/api/health")
def health():
    return {"status": "ok"}

# ============================================================
# EMAIL CHECK
# ============================================================

@app.get("/check/email/{email}")
async def check_email(email: str):
    api_key = os.getenv("LEAKCHECK_API_KEY")
    if not api_key:
        return {"error": "LEAKCHECK_API_KEY не настроен"}

    url = f"https://leakcheck.io/api/public?key={api_key}&check={email}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    data = response.json()

    if not data.get("found"):
        return {"email": email, "breaches": [], "count": 0, "risk": "низкий"}

    sources = data.get("sources", [])
    count = len(sources)
    risk = "низкий" if count == 0 else "средний" if count < 3 else "высокий"

    return {"email": email, "count": count, "risk": risk, "breaches": sources}

# ============================================================
# FAKE DATA
# ============================================================

@app.get("/generate/identity")
def generate_identity():
    return {
        "name": fake.name(),
        "email": fake.email(),
        "phone": fake.phone_number(),
        "birthdate": str(fake.date_of_birth(minimum_age=18, maximum_age=60)),
        "address": fake.address(),
        "username": fake.user_name(),
        "password": fake.password(length=12)
    }

# ============================================================
# USERNAME CHECK
# ============================================================

PLATFORMS = [
    {"name": "GitHub", "url": "https://github.com/{}"},
    {"name": "Twitter", "url": "https://twitter.com/{}"},
    {"name": "Reddit", "url": "https://www.reddit.com/user/{}"},
    {"name": "Instagram", "url": "https://www.instagram.com/{}"},
    {"name": "Facebook", "url": "https://www.facebook.com/{}"},
    {"name": "YouTube", "url": "https://www.youtube.com/@{}"},
    {"name": "TikTok", "url": "https://www.tiktok.com/@{}"},
    {"name": "Twitch", "url": "https://www.twitch.tv/{}"},
    {"name": "Steam", "url": "https://steamcommunity.com/id/{}"},
    {"name": "Telegram", "url": "https://t.me/{}"},
    {"name": "VK", "url": "https://vk.com/{}"},
    {"name": "Pinterest", "url": "https://www.pinterest.com/{}"},
    {"name": "Tumblr", "url": "https://{}.tumblr.com"},
    {"name": "WordPress", "url": "https://{}.wordpress.com"},
    {"name": "Medium", "url": "https://medium.com/@{}"},
    {"name": "LinkedIn", "url": "https://www.linkedin.com/in/{}"},
    {"name": "SoundCloud", "url": "https://soundcloud.com/{}"},
    {"name": "Spotify", "url": "https://open.spotify.com/user/{}"},
    {"name": "Vimeo", "url": "https://vimeo.com/{}"},
    {"name": "Flickr", "url": "https://www.flickr.com/people/{}"},
    {"name": "500px", "url": "https://500px.com/p/{}"},
    {"name": "Gravatar", "url": "https://en.gravatar.com/{}"},
    {"name": "Last.fm", "url": "https://www.last.fm/user/{}"},
    {"name": "Goodreads", "url": "https://www.goodreads.com/{}"},
    {"name": "DeviantArt", "url": "https://{}.deviantart.com"},
    {"name": "Behance", "url": "https://www.behance.net/{}"},
    {"name": "Dribbble", "url": "https://dribbble.com/{}"},
    {"name": "CodePen", "url": "https://codepen.io/{}"},
    {"name": "GitLab", "url": "https://gitlab.com/{}"},
    {"name": "Bitbucket", "url": "https://bitbucket.org/{}"},
    {"name": "SourceForge", "url": "https://sourceforge.net/u/{}"},
    {"name": "Docker Hub", "url": "https://hub.docker.com/u/{}"},
    {"name": "ProductHunt", "url": "https://www.producthunt.com/@{}"},
    {"name": "AngelList", "url": "https://angel.co/{}"},
    {"name": "Keybase", "url": "https://keybase.io/{}"},
    {"name": "Patreon", "url": "https://www.patreon.com/{}"},
    {"name": "PayPal", "url": "https://paypal.me/{}"},
    {"name": "CashApp", "url": "https://cash.app/${}"},
    {"name": "Venmo", "url": "https://venmo.com/{}"},
    {"name": "Wikipedia", "url": "https://en.wikipedia.org/wiki/User:{}"},
    {"name": "Fandom", "url": "https://community.fandom.com/wiki/User:{}"},
    {"name": "Mastodon", "url": "https://mastodon.social/@{}"},
    {"name": "Threads", "url": "https://www.threads.net/@{}"},
    {"name": "Bluesky", "url": "https://bsky.app/profile/{}"},
    {"name": "Roblox", "url": "https://www.roblox.com/search/users?keyword={}"},
    {"name": "Minecraft", "url": "https://namemc.com/profile/{}"},
    {"name": "Xbox", "url": "https://account.xbox.com/profile?gamertag={}"},
    {"name": "PlayStation", "url": "https://psnprofiles.com/{}"},
    {"name": "Nintendo", "url": "https://support.nintendo.com/switch/profile"},
    {"name": "HackerRank", "url": "https://www.hackerrank.com/{}"},
    {"name": "LeetCode", "url": "https://leetcode.com/{}"},
    {"name": "Codeforces", "url": "https://codeforces.com/profile/{}"},
    {"name": "AtCoder", "url": "https://atcoder.jp/users/{}"},
    {"name": "Topcoder", "url": "https://www.topcoder.com/members/{}"},
    {"name": "StackOverflow", "url": "https://stackoverflow.com/users/{}"},
    {"name": "AskUbuntu", "url": "https://askubuntu.com/users/{}"},
    {"name": "SuperUser", "url": "https://superuser.com/users/{}"},
    {"name": "ServerFault", "url": "https://serverfault.com/users/{}"},
    {"name": "Meta StackOverflow", "url": "https://meta.stackoverflow.com/users/{}"},
    {"name": "Habr", "url": "https://habr.com/users/{}"},
    {"name": "Pikabu", "url": "https://pikabu.ru/@{}"},
    {"name": "DTF", "url": "https://dtf.ru/u/{}"},
    {"name": "VC.ru", "url": "https://vc.ru/u/{}"},
    {"name": "Livelib", "url": "https://www.livelib.ru/reader/{}"},
    {"name": "KinoPoisk", "url": "https://www.kinopoisk.ru/user/{}"},
]


@app.get("/check/username/{username}")
async def check_username(username: str):
    found = []
    not_found = []
    errors = []

    async with httpx.AsyncClient(timeout=5.0) as client:
        for platform in PLATFORMS:
            url = platform["url"].format(username)
            try:
                resp = await client.get(url, follow_redirects=True)
                exists = resp.status_code == 200
                result = {"site": platform["name"], "url": url, "exists": exists}
                if exists:
                    found.append(result)
                else:
                    not_found.append(result)
            except Exception:
                errors.append({"site": platform["name"], "url": url, "exists": False, "error": "Ошибка проверки"})

    return {
        "username": username,
        "total_sites_checked": len(PLATFORMS),
        "found": found,
        "not_found": not_found,
        "error_count": len(errors),
        "found_count": len(found),
        "not_found_count": len(not_found),
    }

# ============================================================
# PASSWORD CHECK
# ============================================================

def _calc_password_strength(password: str) -> dict:
    score = 0
    length = len(password)
    issues = []
    suggestions = []

    if length >= 16:
        score += 25
    elif length >= 12:
        score += 20
    elif length >= 8:
        score += 10
    else:
        issues.append("Пароль слишком короткий (менее 8 символов)")
        suggestions.append("Используйте минимум 12 символов")

    has_lower = bool(re.search(r"[a-z]", password))
    has_upper = bool(re.search(r"[A-Z]", password))
    has_digit = bool(re.search(r"\d", password))
    has_special = bool(re.search(r"[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]", password))

    if has_lower: score += 10
    else: suggestions.append("Добавьте строчные буквы")

    if has_upper: score += 15
    else: suggestions.append("Добавьте заглавные буквы")

    if has_digit: score += 15
    else: suggestions.append("Добавьте цифры")

    if has_special: score += 20
    else: suggestions.append("Добавьте спецсимволы (!@#$%^&*)")

    if not re.search(r"(.)\1{2,}", password):
        score += 15
    else:
        issues.append("Есть повторяющиеся символы подряд")

    strength = "очень слабый" if score < 25 else "слабый" if score < 50 else "средний" if score < 75 else "хороший" if score < 90 else "отличный"
    return {"score": min(score, 100), "strength": strength, "length": length, "issues": issues, "suggestions": suggestions}


@app.post("/check/password")
async def check_password(data: dict):
    password = data.get("password", "")
    strength = _calc_password_strength(password)

    # HIBP k-Anonymity
    hibp_found = 0
    hibp_risk = "безопасный"
    hibp_note = ""

    if password:
        sha1 = hashlib.sha1(password.encode()).hexdigest().upper()
        prefix, suffix = sha1[:5], sha1[5:]
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(f"https://api.pwnedpasswords.com/range/{prefix}")
                for line in resp.text.splitlines():
                    if line.split(":")[0] == suffix:
                        hibp_found = int(line.split(":")[1])
                        break
        except Exception:
            pass

        if hibp_found > 1000:
            hibp_risk = "критический"
        elif hibp_found > 100:
            hibp_risk = "высокий"
        elif hibp_found > 10:
            hibp_risk = "средний"
        elif hibp_found > 0:
            hibp_risk = "низкий"

        hibp_note = "Проверка через Have I Been Pwned (k-Anonymity)"

    recommendation = "Пароль надёжный! ✅" if strength["score"] >= 75 and hibp_found == 0 else "Рекомендуем сменить пароль ⚠️"

    return {
        "strength": strength,
        "hibp": {"found": hibp_found > 0, "pwned_count": hibp_found, "risk_level": hibp_risk, "k_anonymity_note": hibp_note},
        "recommendation": recommendation
    }

# ============================================================
# PRIVACY SCORE
# ============================================================

@app.post("/privacy/score")
async def privacy_score(data: dict):
    email = data.get("email")
    username = data.get("username")
    password = data.get("password")

    score = 100
    details = {}
    recommendations = []

    if email:
        api_key = os.getenv("LEAKCHECK_API_KEY")
        breach_count = 0
        if api_key:
            try:
                async with httpx.AsyncClient() as client:
                    resp = await client.get(f"https://leakcheck.io/api/public?key={api_key}&check={email}")
                    rdata = resp.json()
                    breach_count = len(rdata.get("sources", [])) if rdata.get("found") else 0
            except Exception:
                pass

        breach_penalty = min(breach_count * 10, 50)
        score -= breach_penalty
        details["email"] = {"breach_count": breach_count, "breach_penalty": breach_penalty}
        if breach_count > 0:
            recommendations.append(f"Email найден в {breach_count} утечках. Рассмотрите замену.")

    if username:
        spread_count = 0
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                for p in PLATFORMS[:20]:
                    url = p["url"].format(username)
                    try:
                        r = await client.get(url, follow_redirects=True)
                        if r.status_code == 200:
                            spread_count += 1
                    except Exception:
                        pass
        except Exception:
            pass

        spread_penalty = min(spread_count * 3, 30)
        score -= spread_penalty
        details["username"] = {"spread_count": spread_count, "spread_penalty": spread_penalty}
        if spread_count > 5:
            recommendations.append(f"Username найден на {spread_count} платформах. Используйте разные ники.")

    if password:
        pw = _calc_password_strength(password)
        pw_penalty = max(0, 30 - pw["score"] // 3)
        score -= pw_penalty
        details["password"] = {"strength": pw["strength"], "total_password_penalty": pw_penalty}
        if pw["score"] < 50:
            recommendations.append("Пароль слабый. Используйте генератор паролей.")

    total_penalty = 100 - max(score, 0)
    emoji = "🟢" if score >= 80 else "🟡" if score >= 50 else "🔴"

    return {
        "score": max(score, 0),
        "emoji": emoji,
        "total_penalty": total_penalty,
        "details": details,
        "recommendations": recommendations
    }

# ============================================================
# EXIF
# ============================================================

@app.post("/exif/analyze")
async def exif_analyze(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        img = Image.open(io.BytesIO(contents))
        exif_data = img.getexif()

        parsed = {}
        privacy_risks = []

        for tag_id, value in exif_data.items():
            tag = TAGS.get(tag_id, str(tag_id))
            if isinstance(value, bytes):
                value = value.decode("utf-8", errors="replace")
            parsed[tag] = str(value)

            if tag in ("GPSInfo", "GPS"):
                privacy_risks.append("Обнаружены GPS-координаты")
            if "Location" in tag:
                privacy_risks.append(f"Обнаружена локация: {value}")
            if tag == "Software":
                privacy_risks.append(f"ПО может раскрыть устройство: {value}")

        if not privacy_risks and len(parsed) > 3:
            privacy_risks.append("Метаданные могут содержать скрытую информацию")

        risk_level = "высокий" if len(privacy_risks) >= 2 else "средний" if len(privacy_risks) >= 1 else "низкий"

        return {
            "filename": file.filename,
            "exif_count": len(parsed),
            "exif_data": parsed,
            "privacy_risks": privacy_risks,
            "risk_level": risk_level
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка анализа: {str(e)}")


@app.post("/exif/clean")
async def exif_clean(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        img = Image.open(io.BytesIO(contents))

        data = list(img.getdata())
        img_clean = Image.new(img.mode, img.size)
        img_clean.putdata(data)

        buf = io.BytesIO()
        fmt = img.format or "PNG"
        img_clean.save(buf, format=fmt)
        buf.seek(0)

        from fastapi.responses import StreamingResponse
        return StreamingResponse(buf, media_type="image/png", headers={"Content-Disposition": f'attachment; filename="cleaned_{file.filename}"'})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка очистки: {str(e)}")

# ============================================================
# PDF REPORT
# ============================================================

@app.get("/report/generate")
async def generate_report(email: str):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas

        font_path = os.path.join(os.path.dirname(__file__), "fonts", "DejaVuSans.ttf")
        font_file = font_path if os.path.exists(font_path) else None

        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=A4)
        w, h = A4

        if font_file:
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            pdfmetrics.registerFont(TTFont("DejaVu", font_file))
            c.setFont("DejaVu", 18)
        else:
            c.setFont("Helvetica", 18)

        c.drawString(50, h - 50, "Digital Alibi - PDF Report")
        c.drawString(50, h - 80, f"Email: {email}")
        c.save()
        buf.seek(0)

        from fastapi.responses import StreamingResponse
        return StreamingResponse(buf, media_type="application/pdf", headers={"Content-Disposition": f'attachment; filename="report_{email}.pdf"'})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка генерации PDF: {str(e)}")


# ============================================================
# COMPREHENSIVE PDF REPORT (НОВЫЙ ENDPOINT)
# ============================================================

class ComprehensiveReportRequest(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    privacy_score: Optional[dict] = None
    email_breaches: Optional[list] = None
    username_sites: Optional[list] = None


def _add_pdf_page(c, width, height, page_num):
    """Добавляет новую страницу с колонтитулом."""
    c.showPage()
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.gray)
    c.drawString(40, 30, f"Digital Alibi - Report | Page {page_num}")
    c.drawString(width - 200, 30, f"Generated: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    c.setLineWidth(0.5)
    c.setStrokeColor(colors.lightgrey)
    c.line(40, 40, width - 40, 40)
    return height - 60


@app.post("/report/comprehensive")
async def generate_comprehensive_report(data: ComprehensiveReportRequest):
    """Генерирует комплексный PDF-отчёт по всем параметрам."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from reportlab.lib import colors as rl_colors
        from fastapi.responses import StreamingResponse

        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=A4)
        width, height = A4
        y = height - 60

        # --- ТИТУЛЬНАЯ СТРАНИЦА ---
        c.setFillColor(rl_colors.HexColor("#1a1a2e"))
        c.rect(0, 0, width, height, fill=True, stroke=False)

        c.setFillColor(rl_colors.HexColor("#00f0ff"))
        c.setFont("Helvetica-Bold", 32)
        c.drawString(60, height - 180, "DIGITAL ALIBI")

        c.setFillColor(rl_colors.white)
        c.setFont("Helvetica-Bold", 22)
        c.drawString(60, height - 230, "Comprehensive Digital Footprint Report")

        c.setFont("Helvetica", 14)
        c.setFillColor(rl_colors.HexColor("#8888aa"))
        c.drawString(60, height - 270, f"Generated: {datetime.now().strftime('%d.%m.%Y %H:%M')}")

        c.setFont("Helvetica", 12)
        c.setFillColor(rl_colors.white)
        items_y = height - 330
        if data.email:
            c.drawString(60, items_y, f"Email: {data.email}")
            items_y -= 25
        if data.username:
            c.drawString(60, items_y, f"Username: {data.username}")
            items_y -= 25
        if data.password:
            c.drawString(60, items_y, "Password: **** (analyzed)")
            items_y -= 25

        c.setFont("Helvetica", 10)
        c.setFillColor(rl_colors.HexColor("#00ff88"))
        c.drawString(60, 100, "Anti-OSINT Instrument")
        c.setFillColor(rl_colors.HexColor("#8888aa"))
        c.drawString(60, 75, "This report was generated for educational purposes.")

        c.showPage()

        # --- EMAIL SECTION ---
        if data.email:
            y = height - 60
            c.setFillColor(rl_colors.HexColor("#1a1a2e"))
            c.rect(0, height - 80, width, 80, fill=True, stroke=False)
            c.setFillColor(rl_colors.HexColor("#00f0ff"))
            c.setFont("Helvetica-Bold", 20)
            c.drawString(40, height - 45, "1. Email Analysis")

            c.setFillColor(rl_colors.white)
            c.setFont("Helvetica", 12)
            c.drawString(40, height - 70, f"Email: {data.email}")

            y = height - 120

            if data.email_breaches:
                breach_count = len(data.email_breaches)
                risk = "LOW" if breach_count == 0 else "MEDIUM" if breach_count < 3 else "HIGH"
                risk_colors_map = {"LOW": "#2ecc71", "MEDIUM": "#f39c12", "HIGH": "#e74c3c"}

                c.setFillColor(rl_colors.HexColor(risk_colors_map.get(risk, "#888888")))
                c.setFont("Helvetica-Bold", 16)
                c.drawString(40, y, f"Risk Level: {risk}")
                y -= 30

                c.setFillColor(rl_colors.black)
                c.setFont("Helvetica", 13)
                c.drawString(40, y, f"Breaches Found: {breach_count}")
                y -= 35

                if breach_count > 0:
                    c.setFont("Helvetica-Bold", 13)
                    c.drawString(40, y, "Affected Databases:")
                    y -= 25
                    c.setFont("Helvetica", 11)

                    for breach in data.email_breaches:
                        if y < 60:
                            y = _add_pdf_page(c, width, height, 2)
                        if isinstance(breach, dict):
                            name = breach.get("name", "Unknown")
                            date_str = breach.get("date", "")
                            c.drawString(60, y, f"- {name}")
                            if date_str:
                                c.setFillColor(rl_colors.gray)
                                c.drawString(350, y, f"(date: {date_str})")
                                c.setFillColor(rl_colors.black)
                        else:
                            c.drawString(60, y, f"- {breach}")
                        y -= 22
                else:
                    c.setFont("Helvetica", 13)
                    c.setFillColor(rl_colors.HexColor("#2ecc71"))
                    c.drawString(40, y, "OK - Email not found in any known breaches")
            else:
                c.setFont("Helvetica", 12)
                c.setFillColor(rl_colors.gray)
                c.drawString(40, y, "No breach data provided")

        # --- USERNAME SECTION ---
        if data.username:
            c.showPage()
            y = height - 60
            c.setFillColor(rl_colors.HexColor("#1a1a2e"))
            c.rect(0, height - 80, width, 80, fill=True, stroke=False)
            c.setFillColor(rl_colors.HexColor("#00f0ff"))
            c.setFont("Helvetica-Bold", 20)
            c.drawString(40, height - 45, "2. Username Analysis")

            c.setFillColor(rl_colors.white)
            c.setFont("Helvetica", 12)
            c.drawString(40, height - 70, f"Username: {data.username}")

            y = height - 120

            if data.username_sites:
                found = [s for s in data.username_sites if s.get("exists", False)]

                c.setFillColor(rl_colors.black)
                c.setFont("Helvetica-Bold", 14)
                c.drawString(40, y, f"Found on {len(found)} of {len(data.username_sites)} platforms")
                y -= 30

                if found:
                    c.setFont("Helvetica-Bold", 13)
                    c.drawString(40, y, "Detected Accounts:")
                    y -= 25
                    c.setFont("Helvetica", 10)

                    for site in found:
                        if y < 60:
                            y = _add_pdf_page(c, width, height, 3)
                        site_name = site.get("site", "Unknown")
                        site_url = site.get("url", "")
                        c.drawString(60, y, f"- {site_name}")
                        c.setFillColor(rl_colors.HexColor("#0077cc"))
                        c.drawString(250, y, site_url[:60])
                        c.setFillColor(rl_colors.black)
                        y -= 20
                else:
                    c.setFont("Helvetica", 13)
                    c.setFillColor(rl_colors.HexColor("#2ecc71"))
                    c.drawString(40, y, "OK - Username not found on any platform")
            else:
                c.setFont("Helvetica", 12)
                c.setFillColor(rl_colors.gray)
                c.drawString(40, y, "No username data provided")

        # --- PASSWORD SECTION ---
        c.showPage()
        y = height - 60
        c.setFillColor(rl_colors.HexColor("#1a1a2e"))
        c.rect(0, height - 80, width, 80, fill=True, stroke=False)
        c.setFillColor(rl_colors.HexColor("#00f0ff"))
        c.setFont("Helvetica-Bold", 20)
        c.drawString(40, height - 45, "3. Password Analysis")

        y = height - 120

        if data.password:
            pwd = data.password
            pwd_len = len(pwd)
            c.setFillColor(rl_colors.black)
            c.setFont("Helvetica", 12)
            c.drawString(40, y, f"Password length: {pwd_len} characters")
            y -= 30

            criteria = []
            if pwd_len >= 12:
                criteria.append(("Password length: GOOD", "#2ecc71"))
            elif pwd_len >= 8:
                criteria.append(("Password length: MEDIUM", "#f39c12"))
            else:
                criteria.append(("Password length: WEAK", "#e74c3c"))

            checks = [
                (any(ch.islower() for ch in pwd), "Contains lowercase letters", "No lowercase letters"),
                (any(ch.isupper() for ch in pwd), "Contains uppercase letters", "No uppercase letters"),
                (any(ch.isdigit() for ch in pwd), "Contains digits", "No digits"),
                (any(ch in "!@#$%^&*()_+-=[]{}|;:,.<>?/~`" for ch in pwd), "Contains special characters", "No special characters"),
            ]

            for passed, ok_msg, fail_msg in checks:
                if passed:
                    criteria.append((f"OK - {ok_msg}", "#2ecc71"))
                else:
                    criteria.append((f"FAIL - {fail_msg}", "#e74c3c"))

            c.setFont("Helvetica-Bold", 13)
            c.drawString(40, y, "Criteria:")
            y -= 25
            c.setFont("Helvetica", 11)

            for msg, color in criteria:
                c.setFillColor(rl_colors.HexColor(color))
                c.drawString(60, y, msg)
                y -= 22

            # Recommendations
            y -= 10
            c.setFont("Helvetica-Bold", 13)
            c.setFillColor(rl_colors.black)
            c.drawString(40, y, "Recommendations:")
            y -= 25
            c.setFont("Helvetica", 11)
            c.setFillColor(rl_colors.black)

            recs = []
            if pwd_len < 12:
                recs.append("Increase password length to at least 12 characters")
            if not any(ch.isupper() for ch in pwd):
                recs.append("Add uppercase letters (A-Z)")
            if not any(ch.isdigit() for ch in pwd):
                recs.append("Add digits (0-9)")
            if not any(ch in "!@#$%^&*()_+-=[]{}|;:,.<>?/~`" for ch in pwd):
                recs.append("Add special characters (!@#$%...)")
            if pwd_len < 8:
                recs.append("Password is too short! Use at least 8 characters")

            for rec in recs:
                c.drawString(60, y, f"- {rec}")
                y -= 22

            if not recs:
                c.setFillColor(rl_colors.HexColor("#2ecc71"))
                c.drawString(60, y, "OK - Password meets all security criteria")
        else:
            c.setFillColor(rl_colors.gray)
            c.setFont("Helvetica", 12)
            c.drawString(40, y, "Password was not provided for analysis")

        # --- PRIVACY SCORE SECTION ---
        if data.privacy_score:
            c.showPage()
            y = height - 60
            score_data = data.privacy_score
            score_val = score_data.get("score", 0)
            emoji = score_data.get("emoji", "?")

            c.setFillColor(rl_colors.HexColor("#1a1a2e"))
            c.rect(0, height - 80, width, 80, fill=True, stroke=False)
            c.setFillColor(rl_colors.HexColor("#00f0ff"))
            c.setFont("Helvetica-Bold", 20)
            c.drawString(40, height - 45, "4. Overall Privacy Score")

            c.setFillColor(rl_colors.white)
            c.setFont("Helvetica-Bold", 14)
            c.drawString(40, height - 70, f"{emoji} Privacy Score: {score_val} / 100")

            y = height - 120

            c.setFillColor(rl_colors.black)
            c.setFont("Helvetica", 12)
            c.drawString(40, y, f"Total Penalty: {score_data.get('total_penalty', 0)} points")
            y -= 30

            details = score_data.get("details", {})
            if details:
                c.setFont("Helvetica-Bold", 13)
                c.drawString(40, y, "Breakdown:")
                y -= 25
                c.setFont("Helvetica", 11)

                if "email" in details:
                    ed = details["email"]
                    c.drawString(60, y, f"Email: {ed.get('breach_count', 0)} breaches, penalty: -{ed.get('breach_penalty', 0)}")
                    y -= 22
                if "username" in details:
                    ud = details["username"]
                    c.drawString(60, y, f"Username: found on {ud.get('spread_count', 0)} platforms, penalty: -{ud.get('spread_penalty', 0)}")
                    y -= 22
                if "password" in details:
                    pd_data = details["password"]
                    c.drawString(60, y, f"Password: strength: {pd_data.get('strength', 'N/A')}, penalty: -{pd_data.get('total_password_penalty', 0)}")
                    y -= 22

            recs = score_data.get("recommendations", [])
            if recs:
                y -= 10
                c.setFont("Helvetica-Bold", 13)
                c.drawString(40, y, "Recommendations:")
                y -= 25
                c.setFont("Helvetica", 11)
                for rec in recs:
                    c.drawString(60, y, f"- {rec}")
                    y -= 22

        # --- FINAL PAGE: General Recommendations ---
        c.showPage()
        y = height - 60
        c.setFillColor(rl_colors.HexColor("#1a1a2e"))
        c.rect(0, height - 80, width, 80, fill=True, stroke=False)
        c.setFillColor(rl_colors.HexColor("#00f0ff"))
        c.setFont("Helvetica-Bold", 20)
        c.drawString(40, height - 45, "General Security Recommendations")

        y = height - 120
        c.setFillColor(rl_colors.black)
        c.setFont("Helvetica", 11)

        general_recs = [
            "Use a password manager (Bitwarden, KeePass, 1Password)",
            "Enable two-factor authentication (2FA) on all critical services",
            "Use different usernames for different platforms",
            "Consider using disposable email addresses for registration",
            "Regularly check your email for data breaches",
            "Clean EXIF metadata before publishing photos",
            "Use fake data when registering on untrusted websites",
            "Never reuse passwords across multiple sites",
            "Review privacy settings on your social media accounts",
            "Use a VPN or Tor for anonymous browsing",
        ]

        for rec in general_recs:
            if y < 60:
                y = _add_pdf_page(c, width, height, 5)
            c.drawString(60, y, f"- {rec}")
            y -= 24

        y -= 30
        c.setLineWidth(0.5)
        c.setStrokeColor(rl_colors.lightgrey)
        c.line(40, y, width - 40, y)
        y -= 20
        c.setFont("Helvetica", 9)
        c.setFillColor(rl_colors.gray)
        c.drawString(40, y, "This report was generated by Digital Alibi (Anti-OSINT).")
        c.drawString(40, y - 15, "All data was obtained from open sources for educational purposes only.")

        c.save()
        buf.seek(0)

        return StreamingResponse(buf, media_type="application/pdf", headers={"Content-Disposition": 'attachment; filename="digital_alibi_report.pdf"'})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating comprehensive PDF: {str(e)}")

# ============================================================
# IDENTITY MANAGER (PostgreSQL)
# ============================================================

class IdentityCreate(BaseModel):
    label: str
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    birthdate: Optional[str] = None
    address: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None


class IdentityUpdate(BaseModel):
    label: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    birthdate: Optional[str] = None
    address: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None


def _check_pw(password: str) -> str:
    score = sum([
        len(password) >= 8, len(password) >= 12,
        bool(re.search(r"[a-z]", password)), bool(re.search(r"[A-Z]", password)),
        bool(re.search(r"\d", password)), bool(re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", password))
    ])
    return "слабый" if score <= 2 else "средний" if score <= 4 else "сильный"


@app.get("/generate_identity")
def generate_identity_raw():
    pw = fake.password(length=14, special_chars=True, digits=True, upper_case=True, lower_case=True)
    return {
        "name": fake.name(), "email": fake.email(), "phone": fake.phone_number(),
        "birthdate": str(fake.date_of_birth(minimum_age=18, maximum_age=60)),
        "address": fake.address(), "username": fake.user_name(),
        "password": pw, "password_strength": _check_pw(pw),
    }


@app.post("/identities/")
def create_identity(data: IdentityCreate):
    if not DATABASE_URL:
        raise HTTPException(status_code=500, detail="DATABASE_URL не настроен")
    import psycopg2
    from psycopg2.extras import RealDictCursor

    init_db()
    name = data.name or fake.name()
    email = data.email or fake.email()
    phone = data.phone or fake.phone_number()
    birthdate = data.birthdate or str(fake.date_of_birth(minimum_age=18, maximum_age=60))
    address = data.address or fake.address()
    username = data.username or fake.user_name()
    password = data.password or fake.password(length=14, special_chars=True, digits=True, upper_case=True, lower_case=True)
    pw_str = _check_pw(password)

    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO identities (label,name,email,phone,birthdate,address,username,password,password_strength,created_at) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id",
        (data.label, name, email, phone, birthdate, address, username, password, pw_str, datetime.now().isoformat())
    )
    identity_id = cursor.fetchone()[0]
    conn.commit()
    conn.close()

    return {
        "id": identity_id, "label": data.label, "name": name, "email": email,
        "phone": phone, "birthdate": birthdate, "address": address,
        "username": username, "password": password, "password_strength": pw_str,
        "message": "Личность сохранена"
    }


@app.get("/identities/")
def list_identities():
    if not DATABASE_URL:
        raise HTTPException(status_code=500, detail="DATABASE_URL не настроен")
    import psycopg2
    from psycopg2.extras import RealDictCursor

    init_db()
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM identities ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()

    return [dict(r) for r in rows]


@app.get("/identities/{identity_id}")
def get_identity(identity_id: int):
    if not DATABASE_URL:
        raise HTTPException(status_code=500, detail="DATABASE_URL не настроен")
    import psycopg2
    from psycopg2.extras import RealDictCursor

    init_db()
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM identities WHERE id = %s", (identity_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Личность не найдена")
    return dict(row)


@app.put("/identities/{identity_id}")
def update_identity(identity_id: int, data: IdentityUpdate):
    if not DATABASE_URL:
        raise HTTPException(status_code=500, detail="DATABASE_URL не настроен")
    import psycopg2
    from psycopg2.extras import RealDictCursor

    init_db()
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM identities WHERE id = %s", (identity_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Личность не найдена")

    updates = {}
    for field in ["label", "name", "email", "phone", "birthdate", "address", "username"]:
        val = getattr(data, field)
        if val is not None:
            updates[field] = val
    if data.password is not None:
        updates["password"] = data.password
        updates["password_strength"] = _check_pw(data.password)

    if updates:
        set_clause = ", ".join(f"{k} = %s" for k in updates.keys())
        values = list(updates.values()) + [identity_id]
        cursor.execute(f"UPDATE identities SET {set_clause} WHERE id = %s", values)
        conn.commit()
    conn.close()
    return {"message": "Личность обновлена", "id": identity_id}


@app.delete("/identities/{identity_id}")
def delete_identity(identity_id: int):
    if not DATABASE_URL:
        raise HTTPException(status_code=500, detail="DATABASE_URL не настроен")
    import psycopg2

    init_db()
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM identities WHERE id = %s", (identity_id,))
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Личность не найдена")
    conn.commit()
    conn.close()
    return {"message": "Личность удалена", "id": identity_id}


# --- Vercel serverless entry point ---
handler = Mangum(app)
