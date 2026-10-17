import os
import time
import requests
from gnews import GNews

# 1. Получение конфиденциальных данных из переменных окружения (GitHub Secrets)
TELEGRAM_BOT_TOKEN = os.environ.get(8933152399:AAGLu7kLqLd250KmPdKI8kVfp--9_IROyE8)
TELEGRAM_CHAT_ID = os.environ.get(-1004415830609)
GNEWS_API_KEY = os.environ.get(93714938bb2337ea461704e85eb11587)

if not all([TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, GNEWS_API_KEY]):
    raise ValueError("Отсутствуют необходимые переменные среды. Проверьте Secrets в GitHub.")

# 2. Функция отправки сообщения в Telegram
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

# 3. Функция получения новостей
def fetch_news():
    google_news = GNews(language='ru', country='RU', period='1d', max_results=5)
    
    # Можно заменить 'музыка' на 'игры' или 'world' для других тем
    news = google_news.get_news('музыка')
    
    if not news:
        # Если по ключевому слову ничего нет — берём топовые новости
        news = google_news.get_top_news()
    
    articles = []
    for item in news:
        title = item.get('title', 'Без заголовка')
        desc = item.get('description', 'Нет описания')
        link = item.get('url', '#')
        source = item.get('publisher', 'Неизвестный источник')
        
        msg = (
            f"📰 <b>{title}</b>\n\n"
            f"{desc}\n\n"
            f"🔗 <a href='{link}'>Читать далее</a>\n"
            f"📌 Источник: {source}"
        )
        articles.append(msg)
    
    return articles

# 4. Основной процесс
def main():
    print("🚀 Запуск сбора новостей...")
    messages = fetch_news()
    
    if not messages:
        print("ℹ️ Новостей не найдено, задача завершена")
        return

    for msg in messages:
        send_to_telegram(msg)
        time.sleep(2)  # пауза, чтобы не превысить лимиты Telegram

if __name__ == "__main__":
    main()
