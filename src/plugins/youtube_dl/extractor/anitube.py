import re
import xml.etree.ElementTree

from .common import InfoExtractor


class AnitubeIE(InfoExtractor):
    IE_NAME = 'anitube.se'
    _VALID_URL = r'https?://(?:www\.)?anitube\.se/video/(?P<id>\d+)'

    _TEST = {
        'url': 'http://www.anitube.se/video/36621',
        'md5': '59d0eeae28ea0bc8c05e7af429998d43',
        'file': '36621.mp4',
        'info_dict': {
            'id': '36621',
            'ext': 'mp4',
            'title': 'Recorder to Randoseru 01',
        },
        'skip': 'Blocked in the US',
    }

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        video_id = mobj.group('id')

        webpage = self._download_webpage(url, video_id)
        key = self._html_search_regex(r'http://www\.anitube\.se/embed/([A-Za-z0-9_-]*)',
                                      webpage, 'key')

        webpage_config = self._download_webpage('http://www.anitube.se/nuevo/econfig.php?key=%s' % key,
                                                key)
        config_xml = xml.etree.ElementTree.fromstring(webpage_config.encode('utf-8'))

        video_title = config_xml.find('title').text

        formats = []
        video_url = config_xml.find('file')
        if video_url is not None:
            formats.append({
                'format_id': 'sd',
                'url': video_url.text,
            })
        video_url = config_xml.find('filehd')
        if video_url is not None:
            formats.append({
                'format_id': 'hd',
                'url': video_url.text,
            })

        return {
            'id': video_id,
            'title': video_title,
            'formats': formats
        }
