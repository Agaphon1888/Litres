# -*- coding: utf-8 -*-
import os
import time
import requests
from urllib.parse import urlencode

# =========================================================
#    НАСТРОЙКИ – ЗАПОЛНИТЕ ИХ (уже заполнены вами)
# =========================================================
FILE_ID   = "26600058"
USER_ID   = "145468552"
UUID      = "3eba580c-edd4-11e6-9b47-0cc47a5203ba"
ART_ID    = "22872570"

OUTPUT_DIR = "downloaded_pages"
DELAY = 2
MAX_CONSECUTIVE_FAILS = 5

# =========================================================
#           НОВЫЙ КОД С СЕССИЕЙ
# =========================================================

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Referer': 'https://www.litres.ru/',
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

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Создаём сессию – она будет автоматически сохранять и отправлять куки
    session = requests.Session()
    session.headers.update(HEADERS)

    # Сначала заходим на любую страницу сайта, чтобы получить стартовые куки
    print("Получаем начальные куки...")
    try:
        # Заходим на главную litres.ru (или на страницу книги)
        session.get("https://www.litres.ru", timeout=10)
        print("Куки получены.")
    except Exception as e:
        print(f"Не удалось получить начальные куки: {e}")
        # Продолжаем, возможно, куки и не нужны

    page = 0
    fails = 0
    print("Начинаем скачивание...")

    while fails < MAX_CONSECUTIVE_FAILS:
        print(f"Пробуем страницу {page}...")
        success = False

        for fmt in ('jpg', 'gif'):
            url = get_page_url(page, fmt)
            try:
                # Используем сессию для запроса
                resp = session.get(url, timeout=30, stream=True)
                if resp.status_code != 200:
                    continue

                content_type = resp.headers.get('Content-Type', '')
                if fmt == 'jpg' and 'image/jpeg' not in content_type:
                    continue
                if fmt == 'gif' and 'image/gif' not in content_type:
                    continue

                # Если дошли сюда – формат правильный, сохраняем
                filename = os.path.join(OUTPUT_DIR, f"page_{page:03d}.{fmt}")
                with open(filename, 'wb') as f:
                    for chunk in resp.iter_content(8192):
                        f.write(chunk)
                print(f"  -> Страница {page} сохранена как {filename}")
                success = True
                break  # выходим из цикла по форматам

            except Exception as e:
                print(f"  Ошибка {fmt} для стр.{page}: {e}")
                continue

        if success:
            fails = 0
        else:
            print(f"  Не удалось скачать стр.{page}")
            fails += 1

        page += 1
        time.sleep(DELAY)

    print(f"Готово. Всего скачано страниц: {page - fails}")

if __name__ == "__main__":
    main()
