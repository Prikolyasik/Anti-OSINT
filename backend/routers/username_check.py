import httpx
import asyncio
import re
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/check", tags=["Username Check"])


def validate_username(username: str) -> bool:
    """Проверяет корректность формата username."""
    # Разрешаем буквы, цифры, подчёркивание и дефис, длина 3-30 символов
    pattern = r"^[a-zA-Z0-9_-]{3,30}$"
    return re.match(pattern, username) is not None

# Словарь популярных сайтов с шаблонами URL и методами проверки
SITES = [
    {"name": "GitHub", "url": "https://github.com/{}", "check_exists": True,
     "not_found_indicators": ["Not found", "404:", "This is not the page"]},
    {"name": "GitLab", "url": "https://gitlab.com/{}", "check_exists": True,
     "not_found_indicators": ["Not found", "The page you are looking for"]},
    {"name": "Habr", "url": "https://habr.com/ru/users/{}/", "check_exists": True,
     "not_found_indicators": ["Пользователь не найден", "404"]},
    {"name": "Pikabu", "url": "https://pikabu.ru/@{}", "check_exists": True,
     "not_found_indicators": ["Такой страницы не существует", "404"]},
    {"name": "Steam", "url": "https://steamcommunity.com/id/{}", "check_exists": True,
     "not_found_indicators": ["The specified profile is private or does not exist"]},
    {"name": "VK", "url": "https://vk.com/{}", "check_exists": True,
     "not_found_indicators": ["404 Not Found", "Данная страница не найдена"]},
    {"name": "Twitter/X", "url": "https://twitter.com/{}", "check_exists": True,
     "not_found_indicators": ["This account doesn't exist", "Page not found"]},
    {"name": "Reddit", "url": "https://www.reddit.com/user/{}", "check_exists": True,
     "not_found_indicators": ["Sorry, nobody on Reddit goes by that name", "404"]},
    {"name": "Instagram", "url": "https://www.instagram.com/{}/", "check_exists": True,
     "not_found_indicators": ["Sorry, this page isn't available", "Page Not Found"]},
    {"name": "TikTok", "url": "https://www.tiktok.com/@{}", "check_exists": True,
     "not_found_indicators": ["This account doesn't exist"]},
    {"name": "YouTube", "url": "https://www.youtube.com/@{}", "check_exists": True,
     "not_found_indicators": ["404 Not Found", "This page isn't available"]},
    {"name": "Twitch", "url": "https://www.twitch.tv/{}", "check_exists": True,
     "not_found_indicators": ["This channel doesn't exist"]},
    {"name": "Pinterest", "url": "https://www.pinterest.com/{}/", "check_exists": True,
     "not_found_indicators": ["This page is unavailable", "Page not found"]},
    {"name": "Tumblr", "url": "https://{}.tumblr.com/", "check_exists": True,
     "not_found_indicators": ["There's nothing here", "Site not found"]},
    {"name": "WordPress", "url": "https://{}.wordpress.com/", "check_exists": True,
     "not_found_indicators": ["Do you want to register", "No site found"]},
    {"name": "Blogger", "url": "https://{}.blogspot.com/", "check_exists": True,
     "not_found_indicators": ["Sorry, the blog you were looking for does not exist"]},
    {"name": "SoundCloud", "url": "https://soundcloud.com/{}", "check_exists": True,
     "not_found_indicators": ["Sounds like someone got dropped into an unfamiliar place"]},
    {"name": "Spotify", "url": "https://open.spotify.com/user/{}", "check_exists": True,
     "not_found_indicators": ["Page not found", "This page doesn't exist"]},
    {"name": "Telegram", "url": "https://t.me/{}", "check_exists": True,
     "not_found_indicators": ["If you have Telegram", "you can contact", "No one is using this username yet"]},
    {"name": "Mastodon", "url": "https://mastodon.social/@{}", "check_exists": True,
     "not_found_indicators": ["Page not found", "The page you are looking for"]},
    {"name": "Dribbble", "url": "https://dribbble.com/{}", "check_exists": True,
     "not_found_indicators": ["The page you requested doesn't exist"]},
    {"name": "Behance", "url": "https://www.behance.net/{}", "check_exists": True,
     "not_found_indicators": ["404 - Page Not Found", "This profile is not available"]},
    {"name": "Figma", "url": "https://www.figma.com/@{}", "check_exists": True,
     "not_found_indicators": ["This page could not be found"]},
    {"name": "DeviantArt", "url": "https://www.deviantart.com/{}", "check_exists": True,
     "not_found_indicators": ["Page not found", "This user has disabled their profile"]},
    {"name": "Flickr", "url": "https://www.flickr.com/people/{}", "check_exists": True,
     "not_found_indicators": ["Photo not found", "This user has been deleted"]},
    {"name": "500px", "url": "https://500px.com/p/{}", "check_exists": True,
     "not_found_indicators": ["Page not found"]},
    {"name": "Last.fm", "url": "https://www.last.fm/user/{}", "check_exists": True,
     "not_found_indicators": ["This user doesn't exist"]},
    {"name": "Goodreads", "url": "https://www.goodreads.com/{}", "check_exists": True,
     "not_found_indicators": ["Page Not Found", "This user has been deactivated"]},
    {"name": "IMDb", "url": "https://www.imdb.com/user/{}", "check_exists": True,
     "not_found_indicators": ["Page not found", "404 Error"]},
    {"name": "Codecademy", "url": "https://www.codecademy.com/profiles/{}", "check_exists": True,
     "not_found_indicators": ["This profile could not be found"]},
    {"name": "LeetCode", "url": "https://leetcode.com/{}", "check_exists": True,
     "not_found_indicators": ["Page not found", "This user does not exist"]},
    {"name": "Codeforces", "url": "https://codeforces.com/profile/{}", "check_exists": True,
     "not_found_indicators": ["User not found"]},
    {"name": "HackerRank", "url": "https://www.hackerrank.com/{}", "check_exists": True,
     "not_found_indicators": ["This user doesn't exist", "Page not found"]},
    {"name": " itch.io", "url": "https://{}.itch.io/", "check_exists": True,
     "not_found_indicators": ["This page doesn't exist"]},
    {"name": "Roblox", "url": "https://www.roblox.com/user.aspx?username={}", "check_exists": True,
     "not_found_indicators": ["User not found"]},
    {"name": "Minecraft", "url": "https://api.mojang.com/users/profiles/minecraft/{}", "check_exists": False, "api_check": True},
    {"name": "NameMC", "url": "https://namemc.com/profile/{}", "check_exists": True,
     "not_found_indicators": ["Profile not found"]},
    {"name": "Medium", "url": "https://medium.com/@{}", "check_exists": True,
     "not_found_indicators": ["Out of nothing, something", "Page not found"]},
    {"name": "Substack", "url": "https://substack.com/@{}", "check_exists": True,
     "not_found_indicators": ["Page not found"]},
    {"name": "Patreon", "url": "https://www.patreon.com/{}", "check_exists": True,
     "not_found_indicators": ["We couldn't find that page", "Page not found"]},
    {"name": "OnlyFans", "url": "https://onlyfans.com/{}", "check_exists": True,
     "not_found_indicators": ["No posts", "This account doesn't exist"]},
    {"name": "Linktree", "url": "https://linktr.ee/{}", "check_exists": True,
     "not_found_indicators": ["The page you're looking for doesn't exist"]},
    {"name": "Carrd", "url": "https://{}.carrd.co/", "check_exists": True,
     "not_found_indicators": ["This Carrd doesn't exist"]},
    {"name": "About.me", "url": "https://about.me/{}", "check_exists": True,
     "not_found_indicators": ["We can't find that username"]},
    {"name": "Gravatar", "url": "https://en.gravatar.com/{}", "check_exists": True,
     "not_found_indicators": ["Gravatar not found"]},
    {"name": "Keybase", "url": "https://keybase.io/{}", "check_exists": True,
     "not_found_indicators": ["User not found"]},
    {"name": "ProductHunt", "url": "https://www.producthunt.com/@{}", "check_exists": True,
     "not_found_indicators": ["We couldn't find that user"]},
    {"name": "AngelList", "url": "https://angel.co/u/{}", "check_exists": True,
     "not_found_indicators": ["We couldn't find the page you're looking for"]},
]


async def check_site(session: httpx.AsyncClient, username: str, site: dict) -> dict:
    """Проверяет наличие аккаунта на одном сайте."""
    url = site["url"].format(username)
    result = {"site": site["name"], "url": url, "exists": False, "status_code": None, "error": None}

    try:
        response = await session.get(url, follow_redirects=True, timeout=10.0)
        result["status_code"] = response.status_code

        if site.get("api_check"):
            # Для API-проверок (Minecraft) — проверяем JSON ответ
            if response.status_code == 200:
                data = response.json()
                result["exists"] = isinstance(data, dict) and "id" in data
            else:
                result["exists"] = False
        else:
            # Сначала проверяем статус-код
            if response.status_code == 404:
                result["exists"] = False
            elif response.status_code >= 500:
                result["exists"] = False
                result["error"] = f"Ошибка сервера: {response.status_code}"
            else:
                # Для 200-х статусов анализируем контент страницы
                # Если есть not_found_indicators — ищем их в HTML
                not_found_indicators = site.get("not_found_indicators", [])
                page_text = response.text

                # Проверяем наличие маркеров «страница не найдена»
                found_indicator = None
                for indicator in not_found_indicators:
                    if indicator.lower() in page_text.lower():
                        result["exists"] = False
                        found_indicator = indicator
                        break

                # Если маркеров не найдено — считаем что аккаунт существует
                if found_indicator is None:
                    result["exists"] = True

    except httpx.TimeoutException:
        result["error"] = "Таймаут"
    except httpx.RequestError as e:
        result["error"] = str(e)
    except Exception as e:
        result["error"] = str(e)

    return result


@router.get("/username/{username}")
async def check_username(username: str):
    """
    Проверяет наличие аккаунта с данным никнеймом на 48 популярных сайтах.
    Использует многопоточность (asyncio + httpx AsyncClient).
    """
    # Валидация формата username
    if not validate_username(username):
        raise HTTPException(
            status_code=400,
            detail="Некорректный формат username. Разрешены буквы, цифры, _ и -. Длина: 3-30 символов."
        )
    async with httpx.AsyncClient(
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Anti-OSINT/1.0"}
    ) as session:
        tasks = [check_site(session, username, site) for site in SITES]
        results = await asyncio.gather(*tasks)

    found = [r for r in results if r["exists"]]
    not_found = [r for r in results if not r["exists"] and not r["error"]]
    errors = [r for r in results if r["error"]]

    return {
        "username": username,
        "total_sites_checked": len(SITES),
        "found_count": len(found),
        "not_found_count": len(not_found),
        "error_count": len(errors),
        "found": found,
        "not_found": not_found,
        "errors": errors,
    }
