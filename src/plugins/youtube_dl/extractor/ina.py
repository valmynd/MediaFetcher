import re

from .common import InfoExtractor


class InaIE(InfoExtractor):
    """Information Extractor for Ina.fr"""
    _VALID_URL = r'(?:http://)?(?:www\.)?ina\.fr/video/(?P<id>I?[A-F0-9]+)/.*'
    _TEST = {
        'url': 'www.ina.fr/video/I12055569/francois-hollande-je-crois-que-c-est-clair-video.html',
        'file': 'I12055569.mp4',
        'md5': 'a667021bf2b41f8dc6049479d9bb38a3',
        'info_dict': {
            "title": "Fran\u00e7ois Hollande \"Je crois que c'est clair\""
        }
    }

    def _real_extract(self,url):
        mobj = re.match(self._VALID_URL, url)

        video_id = mobj.group('id')
        mrss_url='http://player.ina.fr/notices/%s.mrss' % video_id
        video_extension = 'mp4'
        webpage = self._download_webpage(mrss_url, video_id)

        self.report_extraction(video_id)

        video_url = self._html_search_regex(r'<media:player url="(?P<mp4url>http://mp4.ina.fr/[^"]+\.mp4)',
            webpage, 'video URL')

        video_title = self._search_regex(r'<title><!\[CDATA\[(?P<titre>.*?)]]></title>',
            webpage, 'title')

        return [{
            'id':       video_id,
            'url':      video_url,
            'ext':      video_extension,
            'title':    video_title,
        }]
