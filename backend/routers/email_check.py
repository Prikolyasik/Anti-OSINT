import httpx
import os
from fastapi import APIRouter

router = APIRouter(prefix="/check", tags=["Email Check"])

@router.get("/email/{email}")
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

    return {
        "email": email,
        "count": count,
        "risk": risk,
        "breaches": sources
    }