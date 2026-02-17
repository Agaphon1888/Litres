# -*- coding: utf-8 -*-
import os
import time
import requests
from urllib.parse import urlencode

# =========================================================
#    НАСТРОЙКИ – ЗАПОЛНИТЕ ИХ ВНИМАТЕЛЬНО
# =========================================================

# --- 1. Параметры книги (уже ваши) ---
FILE_ID   = "26600058"
USER_ID   = "145468552"
UUID      = "3eba580c-edd4-11e6-9b47-0cc47a5203ba"
ART_ID    = "22872570"

# --- 2. СВЕЖИЕ куки из браузера (скопируйте прямо перед запуском!) ---
COOKIE_STRING = "вставьте_сюда_СВЕЖИЕ_куки_из_браузера"

# --- 3. Папка и задержка ---
OUTPUT_DIR = "downloaded_pages"
DELAY = 2
MAX_CONSECUTIVE_FAILS = 5

# =========================================================
#           КОД – ТРОГАТЬ НЕ НУЖНО
# =========================================================

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Referer': 'https://www.litres.ru/',
    'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
}

BASE_PARAMS = {
    'file': FILE_ID,
    'user': USER_ID,
    'uuid': UUID,
    'art': ART_ID,
}

def get_page_url(page_num, fmt):
    params = BASE_PARAMS.copy()
    params.update({'page': page_num, 'rt': 'w1900', 'ft': fmt})
    return f"https://www.litres.ru/pages/get_pdf_page/?{urlencode(params)}"

def parse_cookie_string(cookie_str):
    """Превращает строку кук в словарь."""
    cookies = {}
    if cookie_str and cookie_str != "вставьте_сюда_СВЕЖИЕ_куки_из_браузера":
        for item in cookie_str.split('; '):
            if '=' in item:
                key, value = item.split('=', 1)
                cookies[key] = value
    return cookies

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Преобразуем строку кук в словарь
    initial_cookies = parse_cookie_string(COOKIE_STRING)
    if not initial_cookies:
        print("⚠️  ВНИМАНИЕ: куки не заданы или указаны неверно. Скрипт может не работать.")
        print("Скопируйте свежие куки из браузера и вставьте в переменную COOKIE_STRING.")
        return

    # Создаём сессию и загружаем в неё наши куки
    session = requests.Session()
    session.headers.update(HEADERS)
    session.cookies.update(initial_cookies)

    # Делаем пробный запрос к сайту, чтобы сессия подхватила все обновления
    print("Подключаемся к litres.ru для обновления кук...")
    try:
        session.get("https://www.litres.ru", timeout=10)
        print("Куки обновлены.")
    except Exception as e:
        print(f"Предупреждение: не удалось обновить куки, но пробуем дальше. Ошибка: {e}")

    page = 0
    fails = 0
    print("Начинаем скачивание...")

    while fails < MAX_CONSECUTIVE_FAILS:
        print(f"Пробуем страницу {page}...")
        success = False

        for fmt in ('jpg', 'gif'):
            url = get_page_url(page, fmt)
            try:
                resp = session.get(url, timeout=30, stream=True)
                if resp.status_code != 200:
                    continue

                content_type = resp.headers.get('Content-Type', '')
                if fmt == 'jpg' and 'image/jpeg' not in content_type:
                    continue
                if fmt == 'gif' and 'image/gif' not in content_type:
                    continue

                filename = os.path.join(OUTPUT_DIR, f"page_{page:03d}.{fmt}")
                with open(filename, 'wb') as f:
                    for chunk in resp.iter_content(8192):
                        f.write(chunk)
                print(f"  ✅ Страница {page} -> {filename}")
                success = True
                break
            except Exception as e:
                print(f"  Ошибка {fmt} для стр.{page}: {e}")
                continue

        if success:
            fails = 0
        else:
            print(f"  ❌ Не удалось скачать стр.{page}")
            fails += 1

        page += 1
        time.sleep(DELAY)

    print(f"Готово. Всего скачано страниц: {page - fails}")

if __name__ == "__main__":
    main()
