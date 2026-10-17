import os
import sys
import time
import requests
from gnews import GNews

# Читаем секреты из окружения (значения подставит GitHub)
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID   = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
GNEWS_API_KEY      = os.environ.get("GNEWS_API_KEY", "").strip()

missing = []
if not TELEGRAM_BOT_TOKEN:
    missing.append("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_CHAT_ID:
    missing.append("TELEGRAM_CHAT_ID")
if not GNEWS_API_KEY:
    missing.append("GNEWS_API_KEY")

if missing:
    print("❌ Не найдены переменные окружения: " + ", ".join(missing))
    sys.exit(1)


def clean_text(text):
    """Убираем лишние пробелы, переносы и обрезаем слишком длинные описания."""
    if not text:
        return ""
    text = " ".join(text.split())          # схлопываем все пробелы и переносы
    # Обрезаем до 280 символов, чтобы пост был кратким
    if len(text) > 280:
        text = text[:277].rsplit(" ", 1)[0] + "..."
    return text


def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True   # отключаем превью ссылок
    }
    try:
        resp = requests.post(url, json=payload, timeout=30)
        resp.raise_for_status()
        print(f"✅ Отправлено: {text[:60]}...")
    except Exception as e:
        print(f"❌ Ошибка отправки: {e}")


def fetch_news():
    google_news = GNews(language='ru', country='RU', period='1d', max_results=5)
    news = google_news.get_news('музыка')

    if not news:
        news = google_news.get_top_news()

    articles = []
    for item in news:
        title = clean_text(item.get('title', ''))
        desc  = clean_text(item.get('description', ''))

        if not title and not desc:
            continue

        # Формируем краткий пост без ссылок и источников
        if title and desc:
            msg = f"<b>{title}</b>\n\n{desc}"
        elif title:
            msg = f"<b>{title}</b>"
        else:
            msg = desc

        articles.append(msg)

    return articles


def main():
    print("🚀 Запуск сбора новостей...")
    messages = fetch_news()

    if not messages:
        print("ℹ️ Новостей не найдено, задача завершена")
        return

    for msg in messages:
        send_to_telegram(msg)
        time.sleep(2)


if __name__ == "__main__":
    main()
