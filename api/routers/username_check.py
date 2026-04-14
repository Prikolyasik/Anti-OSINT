import httpx
import asyncio
from fastapi import APIRouter

router = APIRouter(prefix="/check", tags=["Username Check"])

# Словарь популярных сайтов с шаблонами URL и методами проверки
SITES = [
    {"name": "GitHub", "url": "https://github.com/{}", "check_exists": True},
    {"name": "GitLab", "url": "https://gitlab.com/{}", "check_exists": True},
    {"name": "Habr", "url": "https://habr.com/ru/users/{}/", "check_exists": True},
    {"name": "Pikabu", "url": "https://pikabu.ru/@{}", "check_exists": True},
    {"name": "Steam", "url": "https://steamcommunity.com/id/{}", "check_exists": True},
    {"name": "VK", "url": "https://vk.com/{}", "check_exists": True},
    {"name": "Twitter/X", "url": "https://twitter.com/{}", "check_exists": True},
    {"name": "Reddit", "url": "https://www.reddit.com/user/{}", "check_exists": True},
    {"name": "Instagram", "url": "https://www.instagram.com/{}/", "check_exists": True},
    {"name": "TikTok", "url": "https://www.tiktok.com/@{}", "check_exists": True},
    {"name": "YouTube", "url": "https://www.youtube.com/@{}", "check_exists": True},
    {"name": "Twitch", "url": "https://www.twitch.tv/{}", "check_exists": True},
    {"name": "Pinterest", "url": "https://www.pinterest.com/{}/", "check_exists": True},
    {"name": "Tumblr", "url": "https://{}.tumblr.com/", "check_exists": True},
    {"name": "WordPress", "url": "https://{}.wordpress.com/", "check_exists": True},
    {"name": "Blogger", "url": "https://{}.blogspot.com/", "check_exists": True},
    {"name": "SoundCloud", "url": "https://soundcloud.com/{}", "check_exists": True},
    {"name": "Spotify", "url": "https://open.spotify.com/user/{}", "check_exists": True},
    {"name": "Telegram", "url": "https://t.me/{}", "check_exists": True},
    {"name": "Mastodon", "url": "https://mastodon.social/@{}", "check_exists": True},
    {"name": "Dribbble", "url": "https://dribbble.com/{}", "check_exists": True},
    {"name": "Behance", "url": "https://www.behance.net/{}", "check_exists": True},
    {"name": "Figma", "url": "https://www.figma.com/@{}", "check_exists": True},
    {"name": "DeviantArt", "url": "https://www.deviantart.com/{}", "check_exists": True},
    {"name": "Flickr", "url": "https://www.flickr.com/people/{}", "check_exists": True},
    {"name": "500px", "url": "https://500px.com/p/{}", "check_exists": True},
    {"name": "Last.fm", "url": "https://www.last.fm/user/{}", "check_exists": True},
    {"name": "Goodreads", "url": "https://www.goodreads.com/{}", "check_exists": True},
    {"name": "IMDb", "url": "https://www.imdb.com/user/{}", "check_exists": True},
    {"name": "Codecademy", "url": "https://www.codecademy.com/profiles/{}", "check_exists": True},
    {"name": "LeetCode", "url": "https://leetcode.com/{}", "check_exists": True},
    {"name": "Codeforces", "url": "https://codeforces.com/profile/{}", "check_exists": True},
    {"name": "HackerRank", "url": "https://www.hackerrank.com/{}", "check_exists": True},
    {"name": " itch.io", "url": "https://{}.itch.io/", "check_exists": True},
    {"name": "Roblox", "url": "https://www.roblox.com/user.aspx?username={}", "check_exists": True},
    {"name": "Minecraft", "url": "https://api.mojang.com/users/profiles/minecraft/{}", "check_exists": False, "api_check": True},
    {"name": "NameMC", "url": "https://namemc.com/profile/{}", "check_exists": True},
    {"name": "Medium", "url": "https://medium.com/@{}", "check_exists": True},
    {"name": "Substack", "url": "https://substack.com/@{}", "check_exists": True},
    {"name": "Patreon", "url": "https://www.patreon.com/{}", "check_exists": True},
    {"name": "OnlyFans", "url": "https://onlyfans.com/{}", "check_exists": True},
    {"name": "Linktree", "url": "https://linktr.ee/{}", "check_exists": True},
    {"name": "Carrd", "url": "https://{}.carrd.co/", "check_exists": True},
    {"name": "About.me", "url": "https://about.me/{}", "check_exists": True},
    {"name": "Gravatar", "url": "https://en.gravatar.com/{}", "check_exists": True},
    {"name": "Keybase", "url": "https://keybase.io/{}", "check_exists": True},
    {"name": "ProductHunt", "url": "https://www.producthunt.com/@{}", "check_exists": True},
    {"name": "AngelList", "url": "https://angel.co/u/{}", "check_exists": True},
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
            # Стандартная проверка: 200 = существует, 404 = нет
            if response.status_code == 200:
                result["exists"] = True
            elif response.status_code == 404:
                result["exists"] = False
            else:
                # Редирект на страницу ошибки тоже может означать отсутствие
                result["exists"] = response.status_code < 400

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
