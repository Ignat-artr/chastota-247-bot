import os
import sys
import time
import requests
from gnews import GNews

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


def send_photo(photo_url, caption):
    """Отправка фото с подписью"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "photo": photo_url,
        "caption": caption,
        "parse_mode": "HTML"
    }
    try:
        resp = requests.post(url, json=payload, timeout=30)
        resp.raise_for_status()
        print(f"✅ Фото отправлено: {caption[:40]}...")
    except Exception as e:
        print(f"❌ Ошибка отправки фото: {e}")
        # Если фото не удалось — отправляем хотя бы текст
        send_text(caption)


def send_text(text):
    """Отправка только текста"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        resp = requests.post(url, json=payload, timeout=30)
        resp.raise_for_status()
        print(f"✅ Текст отправлен: {text[:40]}...")
    except Exception as e:
        print(f"❌ Ошибка отправки текста: {e}")


def fetch_news():
    google_news = GNews(language='ru', country='RU', period='1d', max_results=5)
    news = google_news.get_news('музыка')

    if not news:
        news = google_news.get_top_news()

    return news


def main():
    print("🚀 Запуск...")
    articles = fetch_news()

    if not articles:
        print("ℹ️ Новостей нет")
        return

    for item in articles:
        title = item.get('title', '')
        desc  = item.get('description', '')

        # Убираем хвосты вида " - Название источника" из заголовка
        if ' - ' in title:
            title = title.rsplit(' - ', 1)[0].strip()

        # Короткий текст: заголовок жирным + описание
        text = f"<b>{title}</b>"
        if desc:
            text += f"\n\n{desc}"

        # Пробуем достать картинку из разных возможных полей
        image_url = (
            item.get('image') or
            item.get('image_url') or
            item.get('thumbnail') or
            None
        )

        if image_url and image_url.startswith('http'):
            send_photo(image_url, text)
        else:
            send_text(text)

        time.sleep(3)


if __name__ == "__main__":
    main()
