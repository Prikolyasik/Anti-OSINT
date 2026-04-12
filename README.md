# 🔒 Anti-OSINT / Digital Alibi

Инструмент для проверки email на утечки и генерации фейковых данных для защиты персональной информации.

## Возможности

- ✅ Проверка email по базам утечек (LeakCheck.io)
- ✅ Генерация фейковых персональных данных
- ✅ Создание PDF-отчётов с цифровым следом
- ✅ Кириллическая поддержка в отчётах

## Структура проекта

```
Anti-OSINT/
├── backend/           # FastAPI сервер
│   ├── main.py
│   ├── routers/
│   ├── fonts/         # Шрифты с кириллицей
│   └── reports/       # Генерируемые PDF-отчёты
└── frontend/          # React приложение
```

## Установка

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

3. Настройте API ключ:
```bash
cp .env.example .env
```
Получите API ключ на [LeakCheck.io](https://leakcheck.io/) и вставьте его в `.env`:
```
LEAKCHECK_API_KEY=your_api_key_here
```

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

## Безопасность

- ⚠️ **Никогда не коммитьте файл `.env`** - он содержит секретные ключи
- 📁 Файлы `.env` и `reports/` добавлены в `.gitignore`
- 🔑 Используйте `.env.example` как шаблон для настройки

## Технологии

- **Backend:** FastAPI, httpx, Faker, reportlab
- **Frontend:** React, Axios
- **PDF:** ReportLab с поддержкой кириллицы (DejaVu Sans)

## Лицензия

MIT
