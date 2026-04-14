import hashlib
import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/check", tags=["Password Check"])

HIBP_API_URL = "https://api.pwnedpasswords.com/range/"


class PasswordCheckRequest(BaseModel):
    password: str


def _check_password_strength(password: str) -> dict:
    """Оценивает надёжность пароля по нескольким критериям."""
    score = 0
    issues = []
    suggestions = []

    if len(password) < 8:
        issues.append("Менее 8 символов")
        suggestions.append("Используйте минимум 8 символов")
    else:
        score += 20

    if len(password) >= 12:
        score += 10

    if any(c.islower() for c in password):
        score += 15
    else:
        issues.append("Нет строчных букв")
        suggestions.append("Добавьте строчные буквы (a-z)")

    if any(c.isupper() for c in password):
        score += 15
    else:
        issues.append("Нет заглавных букв")
        suggestions.append("Добавьте заглавные буквы (A-Z)")

    if any(c.isdigit() for c in password):
        score += 15
    else:
        issues.append("Нет цифр")
        suggestions.append("Добавьте цифры (0-9)")

    if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?/~`" for c in password):
        score += 15
    else:
        issues.append("Нет спецсимволов")
        suggestions.append("Добавьте спецсимволы (!@#$%...)")

    # Оценка энтропии (упрощённая)
    charset_size = 0
    if any(c.islower() for c in password):
        charset_size += 26
    if any(c.isupper() for c in password):
        charset_size += 26
    if any(c.isdigit() for c in password):
        charset_size += 10
    if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?/~`" for c in password):
        charset_size += 32

    if charset_size > 0:
        entropy = len(password) * (charset_size.bit_length())
        if entropy >= 80:
            score += 10
        elif entropy >= 60:
            score += 5

    if score >= 80:
        strength = "отличный"
    elif score >= 60:
        strength = "хороший"
    elif score >= 40:
        strength = "средний"
    elif score >= 20:
        strength = "слабый"
    else:
        strength = "очень слабый"

    return {
        "score": score,
        "strength": strength,
        "length": len(password),
        "issues": issues,
        "suggestions": suggestions,
    }


@router.post("/password")
async def check_password(data: PasswordCheckRequest):
    """
    Проверяет пароль через Have I Been Pwned API с использованием k-Anonymity.

    Алгоритм:
    1. Хэшируем пароль алгоритмом SHA-1
    2. Отправляем только первые 5 символов хэша на сервер HIBP
    3. Получаем список всех совпадений (суффиксов хэшей)
    4. Локально проверяем, есть ли наш полный хэш в списке

    Это гарантирует, что сам пароль никогда не передаётся по сети.
    """
    password = data.password

    # Оценка надёжности пароля
    strength_info = _check_password_strength(password)

    # HIBP проверка через k-Anonymity
    sha1_hash = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
    prefix = sha1_hash[:5]
    suffix = sha1_hash[5:]

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(f"{HIBP_API_URL}{prefix}")

    if response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail=f"Ошибка при запросе к HIBP API: HTTP {response.status_code}"
        )

    # Парсим ответ: формат "ХЭШ:КОЛИЧЕСТВО"
    pwned_count = 0
    found_in_hibp = False

    for line in response.text.splitlines():
        if ":" not in line:
            continue
        hash_suffix, count = line.split(":")
        if hash_suffix.upper() == suffix:
            found_in_hibp = True
            pwned_count = int(count)
            break

    # Общая оценка риска
    if found_in_hibp:
        if pwned_count > 10000:
            risk = "критический"
        elif pwned_count > 1000:
            risk = "высокий"
        elif pwned_count > 100:
            risk = "средний"
        else:
            risk = "низкий"
    else:
        risk = "безопасный"

    return {
        "password_length": len(password),
        "strength": strength_info,
        "hibp": {
            "found": found_in_hibp,
            "pwned_count": pwned_count,
            "risk_level": risk,
            "k_anonymity_note": "Полный хэш никогда не передавался — только первые 5 символов",
        },
        "recommendation": (
            "Пароль найден в утечках! Немедленно смените его." if found_in_hibp
            else "Пароль не найден в утечках, но рекомендуется использовать уникальный пароль для каждого сервиса."
        ),
    }
