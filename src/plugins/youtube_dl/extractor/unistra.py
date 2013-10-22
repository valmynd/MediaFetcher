import re

from .common import InfoExtractor

class UnistraIE(InfoExtractor):
    _VALID_URL = r'http://utv.unistra.fr/(?:index|video).php\?id_video\=(\d+)'

    _TEST = {
        'url': 'http://utv.unistra.fr/video.php?id_video=154',
        'file': '154.mp4',
        'md5': '736f605cfdc96724d55bb543ab3ced24',
        'info_dict': {
            'title': 'M!ss Yella',
            'description': 'md5:104892c71bd48e55d70b902736b81bbf',
        },
    }

    def _real_extract(self, url):
        id = re.match(self._VALID_URL, url).group(1)
        webpage = self._download_webpage(url, id)
        file = re.search(r'file: "(.*?)",', webpage).group(1)
        title = self._html_search_regex(r'<title>UTV - (.*?)</', webpage, 'title')

        video_url = 'http://vod-flash.u-strasbg.fr:8080/' + file

        return {'id': id,
                'title': title,
                'ext': 'mp4',
                'url': video_url,
                'description': self._html_search_regex(r'<meta name="Description" content="(.*?)"', webpage, 'description', flags=re.DOTALL),
                'thumbnail': self._search_regex(r'image: "(.*?)"', webpage, 'thumbnail'),
                }
