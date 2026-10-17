import os
import sys
import time
import requests
from gnews import GNews

# Читаем имена переменных из окружения. Значения подставит GitHub из Secrets.
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID   = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
GNEWS_API_KEY      = os.environ.get("GNEWS_API_KEY", "").strip()

# Проверка, что все секреты дошли
missing = []
if not TELEGRAM_BOT_TOKEN:
    missing.append("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_CHAT_ID:
    missing.append("TELEGRAM_CHAT_ID")
if not GNEWS_API_KEY:
    missing.append("GNEWS_API_KEY")

if missing:
    print("❌ Не найдены переменные окружения: " + ", ".join(missing))
    print("Проверьте GitHub → Settings → Secrets and variables → Actions → Repository secrets")
    sys.exit(1)

# Отправка сообщения в Telegram
def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    try:
        resp = requests.post(url, json=payload, timeout=30)
        resp.raise_for_status()
        print(f"✅ Отправлено: {text[:60]}...")
    except Exception as e:
        print(f"❌ Ошибка отправки: {e}")

# Получение новостей
def fetch_news():
    google_news = GNews(language='ru', country='RU', period='1d', max_results=5)
    news = google_news.get_news('музыка')

    if not news:
        news = google_news.get_top_news()

    articles = []
    for item in news:
        title  = item.get('title', 'Без заголовка')
        desc   = item.get('description', 'Нет описания')
        link   = item.get('url', '#')
        source = item.get('publisher', 'Неизвестный источник')

        msg = (
            f"📰 <b>{title}</b>\n\n"
            f"{desc}\n\n"
            f"🔗 <a href='{link}'>Читать далее</a>\n"
            f"📌 Источник: {source}"
        )
        articles.append(msg)

    return articles

# Основной процесс
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
        time.sleep(2)

if __name__ == "__main__":
    main()
