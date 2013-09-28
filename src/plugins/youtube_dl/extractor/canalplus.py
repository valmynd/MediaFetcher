# encoding: utf-8
import re
import xml.etree.ElementTree

from .common import InfoExtractor
from ..utils import unified_strdate

class CanalplusIE(InfoExtractor):
    _VALID_URL = r'https?://(www\.canalplus\.fr/.*?/(?P<path>.*)|player\.canalplus\.fr/#/(?P<id>\d+))'
    _VIDEO_INFO_TEMPLATE = 'http://service.canal-plus.com/video/rest/getVideosLiees/cplus/%s'
    IE_NAME = 'canalplus.fr'

    _TEST = {
        'url': 'http://www.canalplus.fr/c-infos-documentaires/pid1830-c-zapping.html?vid=922470',
        'file': '922470.flv',
        'info_dict': {
            'title': 'Zapping - 26/08/13',
            'description': 'Le meilleur de toutes les chaînes, tous les jours.\nEmission du 26 août 2013',
            'upload_date': '20130826',
        },
        'params': {
            'skip_download': True,
        },
    }

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        video_id = mobj.group('id')
        if video_id is None:
            webpage = self._download_webpage(url, mobj.group('path'))
            video_id = self._search_regex(r'videoId = "(\d+)";', webpage, 'video id')
        info_url = self._VIDEO_INFO_TEMPLATE % video_id
        info_page = self._download_webpage(info_url,video_id, 
                                           'Downloading video info')

        self.report_extraction(video_id)
        doc = xml.etree.ElementTree.fromstring(info_page.encode('utf-8'))
        video_info = [video for video in doc if video.find('ID').text == video_id][0]
        infos = video_info.find('INFOS')
        media = video_info.find('MEDIA')
        formats = [media.find('VIDEOS/%s' % format)
            for format in ['BAS_DEBIT', 'HAUT_DEBIT', 'HD']]
        video_url = [format.text for format in formats if format is not None][-1]

        return {'id': video_id,
                'title': '%s - %s' % (infos.find('TITRAGE/TITRE').text,
                                       infos.find('TITRAGE/SOUS_TITRE').text),
                'url': video_url,
                'ext': 'flv',
                'upload_date': unified_strdate(infos.find('PUBLICATION/DATE').text),
                'thumbnail': media.find('IMAGES/GRAND').text,
                'description': infos.find('DESCRIPTION').text,
                'view_count': int(infos.find('NB_VUES').text),
                }
