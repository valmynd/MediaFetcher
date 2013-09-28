import re
import xml.etree.ElementTree

from .common import InfoExtractor
from ..utils import (
    compat_urllib_parse_urlparse,
    determine_ext,

    ExtractorError,
)


class CollegeHumorIE(InfoExtractor):
    _VALID_URL = r'^(?:https?://)?(?:www\.)?collegehumor\.com/(video|embed|e)/(?P<videoid>[0-9]+)/?(?P<shorttitle>.*)$'

    _TESTS = [{
        'url': 'http://www.collegehumor.com/video/6902724/comic-con-cosplay-catastrophe',
        'file': '6902724.mp4',
        'md5': '1264c12ad95dca142a9f0bf7968105a0',
        'info_dict': {
            'title': 'Comic-Con Cosplay Catastrophe',
            'description': 'Fans get creative this year at San Diego.  Too creative.  And yes, that\'s really Joss Whedon.',
        },
    },
    {
        'url': 'http://www.collegehumor.com/video/3505939/font-conference',
        'file': '3505939.mp4',
        'md5': 'c51ca16b82bb456a4397987791a835f5',
        'info_dict': {
            'title': 'Font Conference',
            'description': 'This video wasn\'t long enough, so we made it double-spaced.',
        },
    }]

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        if mobj is None:
            raise ExtractorError('Invalid URL: %s' % url)
        video_id = mobj.group('videoid')

        info = {
            'id': video_id,
            'uploader': None,
            'upload_date': None,
        }

        self.report_extraction(video_id)
        xmlUrl = 'http://www.collegehumor.com/moogaloop/video/' + video_id
        metaXml = self._download_webpage(xmlUrl, video_id,
                                         'Downloading info XML',
                                         'Unable to download video info XML')

        mdoc = xml.etree.ElementTree.fromstring(metaXml)
        try:
            videoNode = mdoc.findall('./video')[0]
            youtubeIdNode = videoNode.find('./youtubeID')
            if youtubeIdNode is not None:
                return self.url_result(youtubeIdNode.text, 'Youtube')
            info['description'] = videoNode.findall('./description')[0].text
            info['title'] = videoNode.findall('./caption')[0].text
            info['thumbnail'] = videoNode.findall('./thumbnail')[0].text
            next_url = videoNode.findall('./file')[0].text
        except IndexError:
            raise ExtractorError('Invalid metadata XML file')

        if next_url.endswith('manifest.f4m'):
            manifest_url = next_url + '?hdcore=2.10.3'
            manifestXml = self._download_webpage(manifest_url, video_id,
                                         'Downloading XML manifest',
                                         'Unable to download video info XML')

            adoc = xml.etree.ElementTree.fromstring(manifestXml)
            try:
                media_node = adoc.findall('./{http://ns.adobe.com/f4m/1.0}media')[0]
                node_id = media_node.attrib['url']
                video_id = adoc.findall('./{http://ns.adobe.com/f4m/1.0}id')[0].text
            except IndexError as err:
                raise ExtractorError('Invalid manifest file')
            url_pr = compat_urllib_parse_urlparse(info['thumbnail'])
            info['url'] = url_pr.scheme + '://' + url_pr.netloc + video_id[:-2].replace('.csmil','').replace(',','')
            info['ext'] = 'mp4'
        else:
            # Old-style direct links
            info['url'] = next_url
            info['ext'] = determine_ext(info['url'])

        return info
