import json
import re
import xml.etree.ElementTree

from .common import InfoExtractor


class TriluliluIE(InfoExtractor):
    _VALID_URL = r'(?x)(?:https?://)?(?:www\.)?trilulilu\.ro/video-(?P<category>[^/]+)/(?P<video_id>[^/]+)'
    _TEST = {
        "url": "http://www.trilulilu.ro/video-animatie/big-buck-bunny-1",
        'file': "big-buck-bunny-1.mp4",
        'info_dict': {
            "title": "Big Buck Bunny",
            "description": ":) pentru copilul din noi",
        },
        # Server ignores Range headers (--test)
        "params": {
            "skip_download": True
        }
    }

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        video_id = mobj.group('video_id')

        webpage = self._download_webpage(url, video_id)

        title = self._og_search_title(webpage)
        thumbnail = self._og_search_thumbnail(webpage)
        description = self._og_search_description(webpage)

        log_str = self._search_regex(
            r'block_flash_vars[ ]=[ ]({[^}]+})', webpage, 'log info')
        log = json.loads(log_str)

        format_url = ('http://fs%(server)s.trilulilu.ro/%(hash)s/'
                      'video-formats2' % log)
        format_str = self._download_webpage(
            format_url, video_id,
            note='Downloading formats',
            errnote='Error while downloading formats')

        format_doc = xml.etree.ElementTree.fromstring(format_str)
 
        video_url_template = (
            'http://fs%(server)s.trilulilu.ro/stream.php?type=video'
            '&source=site&hash=%(hash)s&username=%(userid)s&'
            'key=ministhebest&format=%%s&sig=&exp=' %
            log)
        formats = [
            {
                'format': fnode.text,
                'url': video_url_template % fnode.text,
                'ext': fnode.text.partition('-')[0]
            }

            for fnode in format_doc.findall('./formats/format')
        ]

        info = {
            '_type': 'video',
            'id': video_id,
            'formats': formats,
            'title': title,
            'description': description,
            'thumbnail': thumbnail,
        }

        # TODO: Remove when #980 has been merged
        info.update(formats[-1])

        return info
