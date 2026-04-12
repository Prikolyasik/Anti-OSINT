import os
import sqlite3
import hashlib
import re
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from faker import Faker

router = APIRouter(prefix="/identities", tags=["Identity Manager"])
fake = Faker("ru_RU")

# Путь к SQLite базе
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "identities.db")


def get_db() -> sqlite3.Connection:
    """Созёт подключение к SQLite базе."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Инициализирует базу данных с таблицами."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS identities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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


# Инициализируем БД при импорте
init_db()


# --- Pydantic модели ---

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


def _check_password_strength(password: str) -> str:
    """Оценивает надёжность пароля."""
    score = 0
    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1
    if re.search(r"[a-z]", password):
        score += 1
    if re.search(r"[A-Z]", password):
        score += 1
    if re.search(r"\d", password):
        score += 1
    if re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", password):
        score += 1

    if score <= 2:
        return "слабый"
    elif score <= 4:
        return "средний"
    else:
        return "сильный"


def _generate_password() -> str:
    """Генерирует надёжный пароль."""
    return fake.password(length=14, special_chars=True, digits=True,
                         upper_case=True, lower_case=True)


@router.get("/generate")
def generate_identity():
    """Генерирует случайную фейковую личность (без сохранения)."""
    password = _generate_password()
    return {
        "name": fake.name(),
        "email": fake.email(),
        "phone": fake.phone_number(),
        "birthdate": str(fake.date_of_birth(minimum_age=18, maximum_age=60)),
        "address": fake.address(),
        "username": fake.user_name(),
        "password": password,
        "password_strength": _check_password_strength(password),
    }


@router.post("/")
def create_identity(data: IdentityCreate):
    """
    Сохраняет личность в базу данных.
    Если поля не указаны — генерирует автоматически.
    """
    name = data.name or fake.name()
    email = data.email or fake.email()
    phone = data.phone or fake.phone_number()
    birthdate = data.birthdate or str(fake.date_of_birth(minimum_age=18, maximum_age=60))
    address = data.address or fake.address()
    username = data.username or fake.user_name()
    password = data.password or _generate_password()
    password_strength = _check_password_strength(password)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO identities (label, name, email, phone, birthdate, address, username, password, password_strength, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (data.label, name, email, phone, birthdate, address, username, password, password_strength, datetime.now().isoformat()))
    conn.commit()
    identity_id = cursor.lastrowid
    conn.close()

    return {
        "id": identity_id,
        "label": data.label,
        "name": name,
        "email": email,
        "phone": phone,
        "birthdate": birthdate,
        "address": address,
        "username": username,
        "password": password,
        "password_strength": password_strength,
        "message": "Личность сохранена"
    }


@router.get("/")
def list_identities():
    """Возвращает список всех сохранённых личностей."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM identities ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "id": row["id"],
            "label": row["label"],
            "name": row["name"],
            "email": row["email"],
            "username": row["username"],
            "password_strength": row["password_strength"],
            "created_at": row["created_at"],
        }
        for row in rows
    ]


@router.get("/{identity_id}")
def get_identity(identity_id: int):
    """Возвращает полную информацию по конкретной личности."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM identities WHERE id = ?", (identity_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Личность не найдена")

    return dict(row)


@router.put("/{identity_id}")
def update_identity(identity_id: int, data: IdentityUpdate):
    """Обновляет данные личности."""
    conn = get_db()
    cursor = conn.cursor()

    # Проверяем существование
    cursor.execute("SELECT * FROM identities WHERE id = ?", (identity_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Личность не найдена")

    # Формируем обновление только переданных полей
    updates = {}
    if data.label is not None:
        updates["label"] = data.label
    if data.name is not None:
        updates["name"] = data.name
    if data.email is not None:
        updates["email"] = data.email
    if data.phone is not None:
        updates["phone"] = data.phone
    if data.birthdate is not None:
        updates["birthdate"] = data.birthdate
    if data.address is not None:
        updates["address"] = data.address
    if data.username is not None:
        updates["username"] = data.username
    if data.password is not None:
        updates["password"] = data.password
        updates["password_strength"] = _check_password_strength(data.password)

    if updates:
        set_clause = ", ".join(f"{k} = ?" for k in updates.keys())
        values = list(updates.values()) + [identity_id]
        cursor.execute(f"UPDATE identities SET {set_clause} WHERE id = ?", values)
        conn.commit()

    conn.close()
    return {"message": "Личность обновлена", "id": identity_id}


@router.delete("/{identity_id}")
def delete_identity(identity_id: int):
    """Удаляет личность из базы."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM identities WHERE id = ?", (identity_id,))
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Личность не найдена")
    conn.commit()
    conn.close()

    return {"message": "Личность удалена", "id": identity_id}
