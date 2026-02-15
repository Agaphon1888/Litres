# -*- coding: utf-8 -*-
"""
Скрипт для скачивания страниц книги с сайта litres.ru.
Перед запуском установите библиотеку requests:
    pip install requests
"""

import os
import time
import requests
from urllib.parse import urlencode

# =========================================================
# НАСТРОЙКИ (заполните своими данными из ссылки на книгу)
# =========================================================

# Эти параметры нужно взять из адресной строки вашей книги
FILE_ID   = "26600058"      # параметр file
USER_ID   = "145468552"     # параметр user
UUID      = "3eba580c-edd4-11e6-9b47-0cc47a5203ba"  # параметр uuid
ART_ID    = "22872570"      # параметр art (можно не указывать, но лучше добавить)
# ART_TYPE = "4"            # параметр art_type, если есть (в вашей ссылке он есть, но может не понадобиться)

# Папка, куда сохранять страницы
OUTPUT_DIR = "downloaded_pages"

# Задержка между запросами (секунды) – чтобы не нагружать сервер
DELAY = 2

# Сколько раз подряд можно получить ошибку, прежде чем считать книгу законченной
MAX_CONSECUTIVE_FAILS = 5

# =========================================================
# ОСНОВНОЙ КОД (лучше не менять)
# =========================================================

# Базовые параметры, которые будут добавлены к каждому запросу
BASE_PARAMS = {
    'file': FILE_ID,
    'user': USER_ID,
    'uuid': UUID,
    'art': ART_ID,
    # 'art_type': ART_TYPE,  # раскомментируйте, если нужно
}

# Заголовки, чтобы имитировать браузер
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Referer': 'https://www.litres.ru/',
}

def get_page_url(page_num, fmt):
    """Формирует полный URL для заданной страницы и формата (jpg/gif)."""
    params = BASE_PARAMS.copy()
    params.update({
        'page': page_num,
        'rt': 'w1900',
        'ft': fmt,
    })
    return f"https://www.litres.ru/pages/get_pdf_page/?{urlencode(params)}"

def try_download(page_num):
    """
    Пытается скачать страницу page_num.
    Сначала пробует формат jpg, если не получается – gif.
    Возвращает True, если страница успешно сохранена.
    """
    for fmt in ('jpg', 'gif'):
        url = get_page_url(page_num, fmt)
        try:
            # Сначала делаем быстрый HEAD-запрос, чтобы проверить доступность и тип
            resp_head = requests.head(url, headers=HEADERS, timeout=10, allow_redirects=True)
            if resp_head.status_code != 200:
                continue  # страница не доступна, пробуем другой формат

            content_type = resp_head.headers.get('Content-Type', '')
            if fmt == 'jpg' and 'image/jpeg' not in content_type and 'image/jpg' not in content_type:
                continue  # сервер вернул не картинку, пробуем gif
            if fmt == 'gif' and 'image/gif' not in content_type:
                continue  # сервер вернул не gif

            # Если дошли сюда – формат подходит, скачиваем
            resp_get = requests.get(url, headers=HEADERS, timeout=30, stream=True)
            resp_get.raise_for_status()

            # Сохраняем в файл
            filename = os.path.join(OUTPUT_DIR, f"page_{page_num:03d}.{fmt}")
            with open(filename, 'wb') as f:
                for chunk in resp_get.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Страница {page_num} сохранена как {filename}")
            return True

        except Exception as e:
            print(f"Ошибка при попытке {fmt} для страницы {page_num}: {e}")
            continue

    print(f"Не удалось скачать страницу {page_num} ни в одном формате.")
    return False

def main():
    # Создаём папку, если её нет
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    page = 0
    fails = 0

    print("Начинаем скачивание...")
    while fails < MAX_CONSECUTIVE_FAILS:
        print(f"Пробуем страницу {page}...")
        success = try_download(page)
        if success:
            fails = 0
        else:
            fails += 1
        page += 1
        time.sleep(DELAY)

    print(f"Скачивание завершено. Всего обработано страниц: {page - fails}")

if __name__ == "__main__":
    main()
