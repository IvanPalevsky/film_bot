# 🎬 Film_Bot

## 📋 О проекте

Telegram-бот, который поможет найти фильм для просмотра на основе ваших предпочтений.

### ✨ Возможности

- 🎯 Случайный выбор фильма
- 🎭 Фильтрация по жанрам
- 📅 Выбор периода выхода фильма
- ⭐ Фильтр по рейтингу
- 🔥 Учет популярности фильма

## 🚀 Как использовать

1. Найдите своего бота в Telegram
2. Нажмите `/start`
3. Настройте предпочтения командой `/settings`
   - Пример: `/settings 2010-2020 7.5 100`
4. Используйте `/search` для поиска фильма
5. Или нажмите кнопку "Случайный фильм"

## 💻 Технологии

- Python
- SQLite3
- pyTelegramBotAPI
- Собственная база фильмов

## 🛠 Установка и запуск

1. Клонируйте репозиторий:
```bash
git clone https://github.com/your-username/movie-roulette-bot.git
```

2. Установите зависимости:
```bash
pip install "название библиотеки"
```

3. Откройте файл `config.py` и добавьте:
```python
TOKEN = 'ваш_токен_бота'
DATABASE = 'путь_к_базе_данных/movie.db'
```

4. Запустите бота:
```bash
python main.py
```

## 📝 Команды бота

- `/start` - Начать работу с ботом
- `/settings [год_начала-год_конца] [оценка] [популярность]` - Настройка параметров поиска
- `/search` - Поиск фильма по заданным параметрам
- `/set_genres` - Выбор предпочитаемых жанров
- `/reset` - Сброс настроек

---
Made by Ваня
