import httpx
import os
import re
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/check", tags=["Email Check"])


def validate_email(email: str) -> bool:
    """Проверяет корректность формата email."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


@router.get("/email/{email}")
async def check_email(email: str):
    # Валидация формата email
    if not validate_email(email):
        raise HTTPException(
            status_code=400,
            detail=f"Некорректный формат email: {email}. Пример: user@example.com"
        )

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

    return {
        "email": email,
        "count": count,
        "risk": risk,
        "breaches": sources
    }