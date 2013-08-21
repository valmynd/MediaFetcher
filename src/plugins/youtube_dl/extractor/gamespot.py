import re
import xml.etree.ElementTree

from .common import InfoExtractor
from ..utils import (
    unified_strdate,
    compat_urllib_parse,
)

class GameSpotIE(InfoExtractor):
    _VALID_URL = r'(?:http://)?(?:www\.)?gamespot\.com/.*-(?P<page_id>\d+)/?'
    _TEST = {
        "url": "http://www.gamespot.com/arma-iii/videos/arma-iii-community-guide-sitrep-i-6410818/",
        "file": "6410818.mp4",
        "md5": "b2a30deaa8654fcccd43713a6b6a4825",
        "info_dict": {
            "title": "Arma III - Community Guide: SITREP I",
            "upload_date": "20130627", 
        }
    }


    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        page_id = mobj.group('page_id')
        webpage = self._download_webpage(url, page_id)
        video_id = self._html_search_regex([r'"og:video" content=".*?\?id=(\d+)"',
                                            r'http://www\.gamespot\.com/videoembed/(\d+)'],
                                           webpage, 'video id')
        data = compat_urllib_parse.urlencode({'id': video_id, 'newplayer': '1'})
        info_url = 'http://www.gamespot.com/pages/video_player/xml.php?' + data
        info_xml = self._download_webpage(info_url, video_id)
        doc = xml.etree.ElementTree.fromstring(info_xml)
        clip_el = doc.find('./playList/clip')

        http_urls = [{'url': node.find('filePath').text,
                      'rate': int(node.find('rate').text)}
            for node in clip_el.find('./httpURI')]
        best_quality = sorted(http_urls, key=lambda f: f['rate'])[-1]
        video_url = best_quality['url']
        title = clip_el.find('./title').text
        ext = video_url.rpartition('.')[2]
        thumbnail_url = clip_el.find('./screenGrabURI').text
        view_count = int(clip_el.find('./views').text)
        upload_date = unified_strdate(clip_el.find('./postDate').text)

        return [{
            'id'          : video_id,
            'url'         : video_url,
            'ext'         : ext,
            'title'       : title,
            'thumbnail'   : thumbnail_url,
            'upload_date' : upload_date,
            'view_count'  : view_count,
        }]
