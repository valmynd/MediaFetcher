import re
import base64

from .common import InfoExtractor


class WimpIE(InfoExtractor):
    _VALID_URL = r'(?:http://)?(?:www\.)?wimp\.com/([^/]+)/'
    _TEST = {
        'url': 'http://www.wimp.com/deerfence/',
        'file': 'deerfence.flv',
        'md5': '8b215e2e0168c6081a1cf84b2846a2b5',
        'info_dict': {
            "title": "Watch Till End: Herd of deer jump over a fence."
        }
    }

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        video_id = mobj.group(1)
        webpage = self._download_webpage(url, video_id)
        title = self._search_regex(r'<meta name="description" content="(.+?)" />',webpage, 'video title')
        thumbnail_url = self._search_regex(r'<meta property="og\:image" content="(.+?)" />', webpage,'video thumbnail')
        googleString = self._search_regex("googleCode = '(.*?)'", webpage, 'file url')
        googleString = base64.b64decode(googleString).decode('ascii')
        final_url = self._search_regex('","(.*?)"', googleString,'final video url')
        ext = final_url.rpartition('.')[2]

        return [{
            'id':        video_id,
            'url':       final_url,
            'ext':       ext,
            'title':     title,
            'thumbnail': thumbnail_url,
        }]

