import os
import sys
import time
import requests
from gnews import GNews

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID   = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
GNEWS_API_KEY      = os.environ.get("GNEWS_API_KEY", "").strip()

missing = []
if not TELEGRAM_BOT_TOKEN: missing.append("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_CHAT_ID:   missing.append("TELEGRAM_CHAT_ID")
if not GNEWS_API_KEY:      missing.append("GNEWS_API_KEY")

if missing:
    print("❌ Не найдены переменные окружения: " + ", ".join(missing))
    sys.exit(1)

def send_photo_with_caption(image_url, caption):
    """Отправка изображения с подписью (без ссылки на источник)"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "photo": image_url,
        "caption": caption,
        "parse_mode": "HTML"
    }
    try:
        resp = requests.post(url, json=payload, timeout=30)
        resp.raise_for_status()
        print(f"✅ Отправлено с фото: {caption[:40]}...")
    except Exception as e:
        print(f"❌ Ошибка отправки фото: {e}")
        # Если фото не отправилось — отправляем только текст
        send_text_only(caption)

def send_text_only(text):
    """Резервный вариант: только текст"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    try:
        resp = requests.post(url, json=payload, timeout=30)
        resp.raise_for_status()
        print(f"✅ Отправлено только текст: {text[:40]}...")
    except Exception as e:
        print(f"❌ Ошибка отправки текста: {e}")

def shorten(text, max_len=150):
    """Обрезка текста до max_len символов"""
    if not text:
        return ""
    text = text.strip()
    if len(text) <= max_len:
        return text
    return text[:max_len].rsplit(' ', 1)[0] + "…"

def fetch_and_send():
    google_news = GNews(language='ru', country='RU', period='1d', max_results=5)
    news = google_news.get_news('музыка')
    if not news:
        news = google_news.get_top_news()

    for item in news:
        title = item.get('title', 'Без заголовка')
        desc = item.get('description', '') or ''
        image_url = item.get('image', '') or item.get('image_url', '')

        # Краткое описание: заголовок + обрезанное описание, без ссылки и источника
        brief = shorten(desc, 150)
        caption = f"<b>{title}</b>\n\n{brief}" if brief else f"<b>{title}</b>"

        # Лимит подписи Telegram — 1024 символа; если больше, обрезаем
        if len(caption) > 1024:
            caption = caption[:1020] + "…"

        if image_url:
            send_photo_with_caption(image_url, caption)
        else:
            send_text_only(caption)

        time.sleep(2)

def main():
    print("🚀 Запуск сбора новостей...")
    fetch_and_send()
    print("✅ Задача завершена")

if __name__ == "__main__":
    main()
