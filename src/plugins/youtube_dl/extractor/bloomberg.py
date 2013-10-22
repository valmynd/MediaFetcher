import re

from .common import InfoExtractor


class BloombergIE(InfoExtractor):
    _VALID_URL = r'https?://www\.bloomberg\.com/video/(?P<name>.+?).html'

    _TEST = {
        'url': 'http://www.bloomberg.com/video/shah-s-presentation-on-foreign-exchange-strategies-qurhIVlJSB6hzkVi229d8g.html',
        'file': '12bzhqZTqQHmmlA8I-i0NpzJgcG5NNYX.mp4',
        'info_dict': {
            'title': 'Shah\'s Presentation on Foreign-Exchange Strategies',
            'description': 'md5:abc86e5236f9f0e4866c59ad36736686',
        },
        'params': {
            # Requires ffmpeg (m3u8 manifest)
            'skip_download': True,
        },
    }

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        name = mobj.group('name')
        webpage = self._download_webpage(url, name)
        ooyala_url = self._og_search_video_url(webpage)
        return self.url_result(ooyala_url, ie='Ooyala')
