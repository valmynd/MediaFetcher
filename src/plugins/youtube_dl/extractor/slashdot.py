import re

from .common import InfoExtractor


class SlashdotIE(InfoExtractor):
    _VALID_URL = r'https?://tv.slashdot.org/video/\?embed=(?P<id>.*?)(&|$)'

    _TEST = {
        'url': 'http://tv.slashdot.org/video/?embed=JscHMzZDplD0p-yNLOzTfzC3Q3xzJaUz',
        'file': 'JscHMzZDplD0p-yNLOzTfzC3Q3xzJaUz.mp4',
        'md5': 'd2222e7a4a4c1541b3e0cf732fb26735',
        'info_dict': {
            'title': ' Meet the Stampede Supercomputing Cluster\'s Administrator',
        },
    }

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        video_id = mobj.group('id')
        webpage = self._download_webpage(url, video_id)
        ooyala_url = self._search_regex(r'<script src="(.*?)"', webpage, 'ooyala url')
        return self.url_result(ooyala_url, 'Ooyala')
