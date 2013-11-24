import os
import re

from .common import InfoExtractor
from ..utils import (
    compat_urllib_parse_urlparse,
    compat_urllib_request,
    compat_urllib_parse,
)
from ..aes import (
    aes_decrypt_text
)

class PornHubIE(InfoExtractor):
    _VALID_URL = r'^(?:https?://)?(?:www\.)?(?P<url>pornhub\.com/view_video\.php\?viewkey=(?P<videoid>[0-9]+))'
    _TEST = {
        'url': 'http://www.pornhub.com/view_video.php?viewkey=648719015',
        'file': '648719015.mp4',
        'md5': '882f488fa1f0026f023f33576004a2ed',
        'info_dict': {
            "uploader": "BABES-COM", 
            "title": "Seductive Indian beauty strips down and fingers her pink pussy",
            "age_limit": 18
        }
    }

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        video_id = mobj.group('videoid')
        url = 'http://www.' + mobj.group('url')

        req = compat_urllib_request.Request(url)
        req.add_header('Cookie', 'age_verified=1')
        webpage = self._download_webpage(req, video_id)

        video_title = self._html_search_regex(r'<h1 [^>]+>([^<]+)', webpage, 'title')
        video_uploader = self._html_search_regex(r'<b>From: </b>(?:\s|<[^>]*>)*(.+?)<', webpage, 'uploader', fatal=False)
        thumbnail = self._html_search_regex(r'"image_url":"([^"]+)', webpage, 'thumbnail', fatal=False)
        if thumbnail:
            thumbnail = compat_urllib_parse.unquote(thumbnail)

        video_urls = list(map(compat_urllib_parse.unquote , re.findall(r'"quality_[0-9]{3}p":"([^"]+)', webpage)))
        if webpage.find('"encrypted":true') != -1:
            password = self._html_search_regex(r'"video_title":"([^"]+)', webpage, 'password').replace('+', ' ')
            video_urls = list([aes_decrypt_text(s, password, 32).decode('utf-8') for s in video_urls])

        formats = []
        for video_url in video_urls:
            path = compat_urllib_parse_urlparse(video_url).path
            extension = os.path.splitext(path)[1][1:]
            format = path.split('/')[5].split('_')[:2]
            format = "-".join(format)
            formats.append({
                'url': video_url,
                'ext': extension,
                'format': format,
                'format_id': format,
            })
        formats.sort(key=lambda format: list([s.zfill(6) for s in format['format'].split('-')]))

        return {
            'id': video_id,
            'uploader': video_uploader,
            'title': video_title,
            'thumbnail': thumbnail,
            'formats': formats,
            'age_limit': 18,
        }
