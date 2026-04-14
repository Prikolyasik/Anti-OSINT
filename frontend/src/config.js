// Конфигурация API
// Для локальной разработки: создайте frontend/.env.local с REACT_APP_API_URL=http://localhost:8000
// Для продакшна на Vercel: задайте переменную окружения REACT_APP_API_URL в настройках проекта

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export default API_URL;
