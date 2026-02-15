import os
import time
import requests
from urllib.parse import urlencode

# --- НАСТРОЙКИ (измените при необходимости) ---
FILE_ID = "26600058"           # ID вашей книги из ссылки
OUTPUT_DIR = "downloaded_pages" # Папка для сохранения
DELAY = 2                       # Задержка между запросами (сек)
TIMEOUT = 15                    # Таймаут запроса
START_PAGE = 0                   # С какой страницы начать (если нужно продолжить)
# ---------------------------------------------

BASE_URL = "https://www.litres.ru/pages/get_pdf_page/"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def get_page_info(page_num):
    """Определяет формат страницы (jpg/gif) и возвращает URL и расширение."""
    # Сначала пробуем как jpg (наиболее частый случай)
    params_jpg = {
        'file': FILE_ID,
        'page': page_num,
        'rt': 'w1900',
        'ft': 'jpg'
    }
    url_jpg = f"{BASE_URL}?{urlencode(params_jpg)}"
    
    try:
        # Делаем легкий HEAD-запрос, чтобы проверить тип контента без скачивания
        response = requests.head(url_jpg, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
        content_type = response.headers.get('Content-Type', '')
        
        if 'image/jpeg' in content_type or 'image/jpg' in content_type:
            return url_jpg, 'jpg'
        elif 'image/gif' in content_type:
            # Если вдруг jpg-запрос вернул gif (маловероятно)
            return url_jpg, 'gif'
        else:
            # Пробуем как gif
            params_gif = params_jpg.copy()
            params_gif['ft'] = 'gif'
            url_gif = f"{BASE_URL}?{urlencode(params_gif)}"
            response_gif = requests.head(url_gif, headers=HEADERS, timeout=TIMEOUT)
            content_type_gif = response_gif.headers.get('Content-Type', '')
            
            if 'image/gif' in content_type_gif:
                return url_gif, 'gif'
            else:
                # Ни тот, ни другой формат не подошёл — возможно, страницы закончились
                return None, None
                
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при проверке страницы {page_num}: {e}")
        return None, None

def download_page(url, page_num, ext):
    """Скачивает страницу и сохраняет в файл."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT, stream=True)
        response.raise_for_status()
        
        filename = os.path.join(OUTPUT_DIR, f"page_{page_num:03d}.{ext}")
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Страница {page_num} сохранена как {filename}")
        return True
    except Exception as e:
        print(f"Не удалось скачать страницу {page_num}: {e}")
        return False

def main():
    # Создаём папку для сохранения
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    page = START_PAGE
    consecutive_fails = 0
    MAX_CONSECUTIVE_FAILS = 5  # Если 5 страниц подряд не найдено, считаем, что книга закончилась
    
    print("Начинаем проверку и скачивание страниц...")
    
    while consecutive_fails < MAX_CONSECUTIVE_FAILS:
        print(f"Проверяем страницу {page}...")
        url, ext = get_page_info(page)
        
        if url and ext:
            if download_page(url, page, ext):
                consecutive_fails = 0  # сбрасываем счётчик ошибок
            else:
                consecutive_fails += 1
        else:
            print(f"Страница {page} не найдена или имеет неизвестный формат.")
            consecutive_fails += 1
        
        page += 1
        time.sleep(DELAY)  # вежливая задержка
    
    print(f"\nСкачивание завершено. Всего обработано страниц: {page - START_PAGE}")

if __name__ == "__main__":
    main()
