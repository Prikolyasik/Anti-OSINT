# 🔒 Anti-OSINT / Digital Alibi

Инструмент для проверки email на утечки и генерации фейковых данных для защиты персональной информации.

## Возможности

- ✅ Проверка email по базам утечек (LeakCheck.io)
- ✅ Генерация фейковых персональных данных
- ✅ Создание PDF-отчётов с цифровым следом
- ✅ Кириллическая поддержка в отчётах
- ✅ Менеджер альтернативных личностей с БД
- ✅ Проверка username на 48+ платформах
- ✅ Анализ паролей (k-Anonymity)
- ✅ EXIF-анализатор и очистка метаданных
- ✅ Комплексный Privacy Score

## Структура проекта

```
Anti-OSINT/
├── backend/           # FastAPI сервер
│   ├── main.py
│   ├── routers/
│   ├── fonts/         # Шрифты с кириллицей
│   └── requirements.txt
├── frontend/          # React приложение
├── vercel.json        # Конфигурация для Vercel
└── .env.example       # Шаблон переменных окружения
```

## Установка (локальная разработка)

### Бэкенд

1. Создайте виртуальное окружение:
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Настройте переменные окружения:

   **Для локальной разработки** — создайте `.env`:
   ```bash
   cp .env.example .env
   ```
   Заполните `.env`:
   ```env
   LEAKCHECK_API_KEY=your_api_key_here
   DATABASE_URL=postgresql://user:password@host/neondb?sslmode=require
   ALLOWED_ORIGINS=http://localhost:3000
   ```

   **Для деплоя на Vercel** — `.env` НЕ нужен. Все переменные задаются в панели Vercel: **Settings → Environment Variables**.

4. Запустите сервер:
```bash
uvicorn main:app --reload
```

### Фронтенд

```bash
cd frontend
npm install
npm start
```

## API Endpoints

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/check/email/{email}` | Проверка email на утечки |
| GET | `/generate/identity` | Генерация фейковой личности |
| GET | `/report/generate?email=` | Создание PDF-отчёта |
| GET | `/check/username/{username}` | Проверка username на платформах |
| POST | `/check/password` | Анализ надёжности пароля |
| POST | `/privacy/score` | Расчёт Privacy Score |
| GET/POST/PUT/DELETE | `/identities/` | Менеджер личностей |
| POST | `/exif/analyze` | Анализ EXIF-метаданных |
| POST | `/exif/clean` | Очистка EXIF и скачивание |

---

## 🚀 Деплой на Vercel

### Предварительные требования

1. **База данных** — проект использует **PostgreSQL (Neon)**.
   - Зарегистрируйтесь на [neon.tech](https://neon.tech)
   - Создайте проект и получите `DATABASE_URL`
   - ⚠️ **SQLite больше не используется** — он не работает в serverless

2. **API ключ LeakCheck.io** — получите на [leakcheck.io](https://leakcheck.io/)

### Шаги деплоя

#### 1. Подключите репозиторий к Vercel

```bash
npm i -g vercel
vercel
```

Или через веб-интерфейс: [vercel.com/new](https://vercel.com/new) → Import Git Repository

#### 2. Настройте переменные окружения в Vercel

В панели Vercel: **Settings → Environment Variables** добавьте:

| Переменная | Описание | Пример |
|---|---|---|
| `DATABASE_URL` | Подключение к PostgreSQL | `postgresql://user:pass@host/neondb?sslmode=require` |
| `LEAKCHECK_API_KEY` | API ключ LeakCheck | `cdaf766358670...` |
| `ALLOWED_ORIGINS` | CORS origins (через запятую) | `https://my-app.vercel.app` |
| `REACT_APP_API_URL` | URL API для фронтенда | `/api` (относительный путь) |

#### 3. Деплой

```bash
vercel --prod
```

Vercel автоматически:
- Соберёт фронтенд через `npm run vercel-build`
- Запустит FastAPI через serverless функцию с Mangum

### Локальная переменная окружения для фронтенда

Создайте `frontend/.env.local`:
```env
REACT_APP_API_URL=http://localhost:8000
```

---

## Безопасность

- ⚠️ **Никогда не коммитьте файл `.env`** - он содержит секретные ключи
- 📁 Файлы `.env` и `reports/` добавлены в `.gitignore`
- 🔑 Используйте `.env.example` как шаблон для настройки
- 🔄 **Сразу смените пароль от БД** если он попал в лог/commit

## Технологии

- **Backend:** FastAPI, httpx, Faker, reportlab, psycopg2, mangum
- **Frontend:** React, Axios, Recharts, Framer Motion
- **Database:** PostgreSQL (Neon)
- **PDF:** ReportLab с поддержкой кириллицы (DejaVu Sans)
- **Deploy:** Vercel (serverless)

## Лицензия

MIT
