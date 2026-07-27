import random
import string
import requests

def gen_pass(length=10):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def gen_emodji():
    emojis = ['😊', '😂', '🤣', '❤️', '😍', '🤔', '😎', '🥳', '😈', '👻']
    return random.choice(emojis)

def flip_coin():
    return random.choice(['орёл', 'решка'])

# Ваш ключ Pixabay
PIXABAY_API_KEY = "56873873-dbfdaf56d22446e56c13d64cc"

def search_images(query, per_page=3):
    url = "https://pixabay.com/api/"
    params = {
        "key": PIXABAY_API_KEY,
        "q": query,
        "per_page": per_page,
        "image_type": "photo",
        "safesearch": "true"
    }
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        images = []
        for hit in data.get("hits", []):
            images.append({
                "id": str(hit["id"]),
                "url": hit["webformatURL"],
                "thumb": hit["previewURL"]
            })
        return images
    except requests.exceptions.RequestException as e:
        raise Exception(f"Ошибка при запросе к Pixabay API: {e}")

def download_image(url):
    """Скачивает изображение, возвращает байты или None."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://www.bing.com/',  # можно оставить, не мешает
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8'
        }
        response = requests.get(url, headers=headers, timeout=15, stream=True)
        if response.status_code != 200:
            return None
        content_type = response.headers.get('content-type', '').lower()
        if 'image' not in content_type:
            return None
        content = response.content
        if len(content) < 100:
            return None
        # Проверка сигнатур (можно оставить)
        if (content[:3] == b'\xff\xd8\xff' or
            content[:4] == b'\x89PNG' or
            content[:3] == b'GIF' or
            (content[:4] == b'RIFF' and content[8:12] == b'WEBP') or
            content[:2] == b'BM'):
            return content
        if 'image' in content_type:
            return content
        return None
    except Exception:
        return None