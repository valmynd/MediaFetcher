import re
import xml.etree.ElementTree

from .common import InfoExtractor
from ..utils import determine_ext


class EbaumsWorldIE(InfoExtractor):
    _VALID_URL = r'https?://www\.ebaumsworld\.com/video/watch/(?P<id>\d+)'

    _TEST = {
        'url': 'http://www.ebaumsworld.com/video/watch/83367677/',
        'file': '83367677.mp4',
        'info_dict': {
            'title': 'A Giant Python Opens The Door',
            'description': 'This is how nightmares start...',
            'uploader': 'jihadpizza',
        },
    }

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        video_id = mobj.group('id')
        config_xml = self._download_webpage(
            'http://www.ebaumsworld.com/video/player/%s' % video_id, video_id)
        config = xml.etree.ElementTree.fromstring(config_xml.encode('utf-8'))
        video_url = config.find('file').text

        return {
            'id': video_id,
            'title': config.find('title').text,
            'url': video_url,
            'ext': determine_ext(video_url),
            'description': config.find('description').text,
            'thumbnail': config.find('image').text,
            'uploader': config.find('username').text,
        }
