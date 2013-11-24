import re
import json

from .common import InfoExtractor
from ..utils import (
    compat_str,
)


class MySpaceIE(InfoExtractor):
    _VALID_URL = r'https?://myspace\.com/([^/]+)/video/[^/]+/(?P<id>\d+)'

    _TEST = {
        'url': 'https://myspace.com/coldplay/video/viva-la-vida/100008689',
        'info_dict': {
            'id': '100008689',
            'ext': 'flv',
            'title': 'Viva La Vida',
            'description': 'The official Viva La Vida video, directed by Hype Williams',
            'uploader': 'Coldplay',
            'uploader_id': 'coldplay',
        },
        'params': {
            # rtmp download
            'skip_download': True,
        },
    }

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        video_id = mobj.group('id')
        webpage = self._download_webpage(url, video_id)
        context = json.loads(self._search_regex(r'context = ({.*?});', webpage,
            'context'))
        video = context['video']
        rtmp_url, play_path = video['streamUrl'].split(';', 1)

        return {
            'id': compat_str(video['mediaId']),
            'title': video['title'],
            'url': rtmp_url,
            'play_path': play_path,
            'ext': 'flv',
            'description': video['description'],
            'thumbnail': video['imageUrl'],
            'uploader': video['artistName'],
            'uploader_id': video['artistUsername'],
        }
