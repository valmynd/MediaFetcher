import os
import re

from .common import InfoExtractor
from ..utils import (
    compat_urllib_parse_urlparse,
    compat_urllib_request,
)
from ..aes import (
    aes_decrypt_text
)

class Tube8IE(InfoExtractor):
    _VALID_URL = r'^(?:https?://)?(?:www\.)?(?P<url>tube8\.com/[^/]+/[^/]+/(?P<videoid>[0-9]+)/?)'
    _TEST = {
        'url': 'http://www.tube8.com/teen/kasia-music-video/229795/',
        'file': '229795.mp4',
        'md5': 'e9e0b0c86734e5e3766e653509475db0',
        'info_dict': {
            "description": "hot teen Kasia grinding", 
            "uploader": "unknown", 
            "title": "Kasia music video",
            "age_limit": 18,
        }
    }

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        video_id = mobj.group('videoid')
        url = 'http://www.' + mobj.group('url')

        req = compat_urllib_request.Request(url)
        req.add_header('Cookie', 'age_verified=1')
        webpage = self._download_webpage(req, video_id)

        video_title = self._html_search_regex(r'videotitle	="([^"]+)', webpage, 'title')
        video_description = self._html_search_regex(r'>Description:</strong>(.+?)<', webpage, 'description', fatal=False)
        video_uploader = self._html_search_regex(r'>Submitted by:</strong>(?:\s|<[^>]*>)*(.+?)<', webpage, 'uploader', fatal=False)
        thumbnail = self._html_search_regex(r'"image_url":"([^"]+)', webpage, 'thumbnail', fatal=False)
        if thumbnail:
            thumbnail = thumbnail.replace('\\/', '/')

        video_url = self._html_search_regex(r'"video_url":"([^"]+)', webpage, 'video_url')
        if webpage.find('"encrypted":true')!=-1:
            password = self._html_search_regex(r'"video_title":"([^"]+)', webpage, 'password')
            video_url = aes_decrypt_text(video_url, password, 32).decode('utf-8')
        path = compat_urllib_parse_urlparse(video_url).path
        extension = os.path.splitext(path)[1][1:]
        format = path.split('/')[4].split('_')[:2]
        format = "-".join(format)

        return {
            'id': video_id,
            'uploader': video_uploader,
            'title': video_title,
            'thumbnail': thumbnail,
            'description': video_description,
            'url': video_url,
            'ext': extension,
            'format': format,
            'format_id': format,
            'age_limit': 18,
        }
