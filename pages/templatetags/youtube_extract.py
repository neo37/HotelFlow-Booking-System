import re
from django import template
from urllib.parse import urlparse, parse_qs

register = template.Library()


@register.filter
def youtube_id(url):
    """Извлекает ID видео из URL YouTube"""
    if not url:
        return None
    
    # Убираем пробелы
    url = url.strip()
    
    # Различные форматы YouTube URL
    patterns = [
        # youtube.com/watch?v=VIDEO_ID
        r'(?:youtube\.com\/watch\?v=)([a-zA-Z0-9_-]{11})',
        # youtu.be/VIDEO_ID
        r'(?:youtu\.be\/)([a-zA-Z0-9_-]{11})',
        # youtube.com/embed/VIDEO_ID
        r'(?:youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
        # youtube.com/v/VIDEO_ID
        r'(?:youtube\.com\/v\/)([a-zA-Z0-9_-]{11})',
        # youtube.com/watch?feature=player_embedded&v=VIDEO_ID
        r'(?:youtube\.com\/watch\?.*v=)([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            video_id = match.group(1)
            # Проверяем, что ID имеет правильную длину (11 символов)
            if len(video_id) == 11:
                return video_id
    
    # Пробуем извлечь через parse_qs для сложных URL
    try:
        parsed = urlparse(url)
        if 'youtube.com' in parsed.netloc or 'youtu.be' in parsed.netloc:
            if 'youtu.be' in parsed.netloc:
                # Для youtu.be/VIDEO_ID
                path = parsed.path.strip('/')
                if path and len(path) == 11:
                    return path
            else:
                # Для youtube.com/watch?v=VIDEO_ID
                query_params = parse_qs(parsed.query)
                if 'v' in query_params:
                    video_id = query_params['v'][0]
                    if len(video_id) == 11:
                        return video_id
    except:
        pass
    
    return None

