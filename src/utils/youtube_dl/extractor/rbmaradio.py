import json
import re

from .common import InfoExtractor
from ..utils import (
    compat_urllib_parse_urlparse,

    ExtractorError,
)


class RBMARadioIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?rbmaradio\.com/shows/(?P<videoID>[^/]+)$'
    _TEST = {
        'url': 'http://www.rbmaradio.com/shows/ford-lopatin-live-at-primavera-sound-2011',
        'file': 'ford-lopatin-live-at-primavera-sound-2011.mp3',
        'md5': '6bc6f9bcb18994b4c983bc3bf4384d95',
        'info_dict': {
            "uploader_id": "ford-lopatin", 
            "location": "Spain", 
            "description": "Joel Ford and Daniel \u2019Oneohtrix Point Never\u2019 Lopatin fly their midified pop extravaganza to Spain. Live at Primavera Sound 2011.", 
            "uploader": "Ford & Lopatin", 
            "title": "Live at Primavera Sound 2011"
        }
    }

    def _real_extract(self, url):
        m = re.match(self._VALID_URL, url)
        video_id = m.group('videoID')

        webpage = self._download_webpage(url, video_id)

        json_data = self._search_regex(r'window\.gon.*?gon\.show=(.+?);$',
            webpage, 'json data', flags=re.MULTILINE)

        try:
            data = json.loads(json_data)
        except ValueError as e:
            raise ExtractorError('Invalid JSON: ' + str(e))

        video_url = data['akamai_url'] + '&cbr=256'
        url_parts = compat_urllib_parse_urlparse(video_url)
        video_ext = url_parts.path.rpartition('.')[2]
        info = {
                'id': video_id,
                'url': video_url,
                'ext': video_ext,
                'title': data['title'],
                'description': data.get('teaser_text'),
                'location': data.get('country_of_origin'),
                'uploader': data.get('host', {}).get('name'),
                'uploader_id': data.get('host', {}).get('slug'),
                'thumbnail': data.get('image', {}).get('large_url_2x'),
                'duration': data.get('duration'),
        }
        return [info]
