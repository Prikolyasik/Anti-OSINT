import hashlib
import httpx
import asyncio
import os
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/privacy", tags=["Privacy Score"])


class PrivacyScoreRequest(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None


async def _check_email_breaches(email: str) -> dict:
    """Проверяет email через LeakCheck API."""
    api_key = os.getenv("LEAKCHECK_API_KEY")
    if not api_key:
        return {"email": email, "error": "LEAKCHECK_API_KEY не настроен", "breach_penalty": 0}

    url = f"https://leakcheck.io/api/public?key={api_key}&check={email}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)

    data = response.json()
    breach_count = 0
    if data.get("found"):
        breach_count = len(data.get("sources", []))

    # Штраф: -20 баллов за каждую утечку (макс -60)
    breach_penalty = min(breach_count * 20, 60)

    return {
        "email": email,
        "breach_count": breach_count,
        "breach_penalty": breach_penalty,
    }


async def _check_username_spread(username: str) -> dict:
    """Проверяет «разбросанность» никнейма по сайтам."""
    # Упрощённая проверка — используем тот же список сайтов, что и в username_check
    from routers.username_check import SITES, check_site

    async with httpx.AsyncClient(
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Anti-OSINT/1.0"}
    ) as session:
        tasks = [check_site(session, username, site) for site in SITES]
        results = await asyncio.gather(*tasks)

    found_count = sum(1 for r in results if r["exists"])

    # Штраф: -10 баллов если никнейм найден на 10+ сайтах
    if found_count >= 20:
        spread_penalty = 30
    elif found_count >= 10:
        spread_penalty = 20
    elif found_count >= 5:
        spread_penalty = 10
    else:
        spread_penalty = 0

    return {
        "username": username,
        "found_on_sites": found_count,
        "spread_penalty": spread_penalty,
    }


async def _check_password_security(password: str) -> dict:
    """Проверяет пароль через HIBP."""
    sha1_hash = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
    prefix = sha1_hash[:5]
    suffix = sha1_hash[5:]

    hibp_penalty = 0
    pwned_count = 0

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"https://api.pwnedpasswords.com/range/{prefix}")

        if response.status_code == 200:
            for line in response.text.splitlines():
                if ":" not in line:
                    continue
                hash_suffix, count = line.split(":")
                if hash_suffix.upper() == suffix:
                    pwned_count = int(count)
                    break

        # Штраф за утечку пароля
        if pwned_count > 10000:
            hibp_penalty = 30
        elif pwned_count > 1000:
            hibp_penalty = 25
        elif pwned_count > 100:
            hibp_penalty = 20
        elif pwned_count > 0:
            hibp_penalty = 10
    except Exception:
        pass

    # Оценка длины пароля
    password_length = len(password)
    length_penalty = 0
    if password_length < 6:
        length_penalty = 15
    elif password_length < 8:
        length_penalty = 10
    elif password_length < 12:
        length_penalty = 5

    return {
        "password_length": password_length,
        "pwned_count": pwned_count,
        "hibp_penalty": hibp_penalty,
        "length_penalty": length_penalty,
        "total_password_penalty": hibp_penalty + length_penalty,
    }


@router.post("/score")
async def calculate_privacy_score(data: PrivacyScoreRequest):
    """
    Агрегирующий endpoint — рассчитывает «Рейтинг приватности» от 0 до 100.
    """
    total_penalty = 0
    details = {}

    # Параллельная проверка всех переданных параметров
    tasks = {}

    if data.email:
        tasks["email"] = asyncio.create_task(_check_email_breaches(data.email))
    if data.username:
        tasks["username"] = asyncio.create_task(_check_username_spread(data.username))
    if data.password:
        tasks["password"] = asyncio.create_task(_check_password_security(data.password))

    if tasks:
        results = await asyncio.gather(*tasks.values())
        for key, result in zip(tasks.keys(), results):
            details[key] = result
            if key == "email":
                total_penalty += result["breach_penalty"]
            elif key == "username":
                total_penalty += result["spread_penalty"]
            elif key == "password":
                total_penalty += result["total_password_penalty"]

    score = max(100 - total_penalty, 0)

    # Классификация
    if score >= 80:
        rating = "отлично"
        emoji = "🟢"
    elif score >= 60:
        rating = "хорошо"
        emoji = "🟡"
    elif score >= 40:
        rating = "удовлетворительно"
        emoji = "🟠"
    elif score >= 20:
        rating = "плохо"
        emoji = "🔴"
    else:
        rating = "критично"
        emoji = "⚫"

    # Генерация рекомендаций
    recommendations = []
    if details.get("email", {}).get("breach_count", 0) > 0:
        recommendations.append("🔒 Смените пароль на всех сервисах, где использовался этот email")
        recommendations.append("📧 Рассмотрите использование одноразовых email-адресов")
    if details.get("username", {}).get("found_on_sites", 0) >= 10:
        recommendations.append("👤 Используйте разные никнеймы для разных платформ")
        recommendations.append("🛡️ Рассмотрите генератор фейковых личностей для регистрации")
    if details.get("password", {}).get("pwned_count", 0) > 0:
        recommendations.append("🔑 Этот пароль скомпрометирован — немедленно смените его")
    if details.get("password", {}).get("password_length", 0) < 12:
        recommendations.append("📝 Используйте пароли длиной минимум 12 символов")

    if not recommendations:
        recommendations.append("✅ Ваш цифровой след в порядке! Продолжайте следить за приватностью.")

    return {
        "score": score,
        "rating": rating,
        "emoji": emoji,
        "total_penalty": total_penalty,
        "details": details,
        "recommendations": recommendations,
    }
