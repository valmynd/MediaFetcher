# encoding: utf-8

import re
import json
import xml.etree.ElementTree

from .common import InfoExtractor
from ..utils import (
    compat_urllib_parse,
    find_xpath_attr,
    compat_urlparse,

    ExtractorError,
)

class BrightcoveIE(InfoExtractor):
    _VALID_URL = r'https?://.*brightcove\.com/(services|viewer).*\?(?P<query>.*)'
    _FEDERATED_URL_TEMPLATE = 'http://c.brightcove.com/services/viewer/htmlFederated?%s'
    _PLAYLIST_URL_TEMPLATE = 'http://c.brightcove.com/services/json/experience/runtime/?command=get_programming_for_experience&playerKey=%s'

    _TESTS = [
        {
            # From http://www.8tv.cat/8aldia/videos/xavier-sala-i-martin-aquesta-tarda-a-8-al-dia/
            'url': 'http://c.brightcove.com/services/viewer/htmlFederated?playerID=1654948606001&flashID=myExperience&%40videoPlayer=2371591881001',
            'file': '2371591881001.mp4',
            'md5': '9e80619e0a94663f0bdc849b4566af19',
            'note': 'Test Brightcove downloads and detection in GenericIE',
            'info_dict': {
                'title': 'Xavier Sala i Martín: “Un banc que no presta és un banc zombi que no serveix per a res”',
                'uploader': '8TV',
                'description': 'md5:a950cc4285c43e44d763d036710cd9cd',
            }
        },
        {
            # From http://medianetwork.oracle.com/video/player/1785452137001
            'url': 'http://c.brightcove.com/services/viewer/htmlFederated?playerID=1217746023001&flashID=myPlayer&%40videoPlayer=1785452137001',
            'file': '1785452137001.flv',
            'info_dict': {
                'title': 'JVMLS 2012: Arrays 2.0 - Opportunities and Challenges',
                'description': 'John Rose speaks at the JVM Language Summit, August 1, 2012.',
                'uploader': 'Oracle',
            },
        },
    ]

    @classmethod
    def _build_brighcove_url(cls, object_str):
        """
        Build a Brightcove url from a xml string containing
        <object class="BrightcoveExperience">{params}</object>
        """

        # Fix up some stupid HTML, see https://github.com/rg3/youtube-dl/issues/1553
        object_str = re.sub(r'(<param name="[^"]+" value="[^"]+")>',
                            lambda m: m.group(1) + '/>', object_str)
        # Fix up some stupid XML, see https://github.com/rg3/youtube-dl/issues/1608
        object_str = object_str.replace('<--', '<!--')

        object_doc = xml.etree.ElementTree.fromstring(object_str)
        assert 'BrightcoveExperience' in object_doc.attrib['class']
        params = {'flashID': object_doc.attrib['id'],
                  'playerID': find_xpath_attr(object_doc, './param', 'name', 'playerID').attrib['value'],
                  }
        playerKey = find_xpath_attr(object_doc, './param', 'name', 'playerKey')
        # Not all pages define this value
        if playerKey is not None:
            params['playerKey'] = playerKey.attrib['value']
        videoPlayer = find_xpath_attr(object_doc, './param', 'name', '@videoPlayer')
        if videoPlayer is not None:
            params['@videoPlayer'] = videoPlayer.attrib['value']
        data = compat_urllib_parse.urlencode(params)
        return cls._FEDERATED_URL_TEMPLATE % data

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        query_str = mobj.group('query')
        query = compat_urlparse.parse_qs(query_str)

        videoPlayer = query.get('@videoPlayer')
        if videoPlayer:
            return self._get_video_info(videoPlayer[0], query_str)
        else:
            player_key = query['playerKey']
            return self._get_playlist_info(player_key[0])

    def _get_video_info(self, video_id, query):
        request_url = self._FEDERATED_URL_TEMPLATE % query
        webpage = self._download_webpage(request_url, video_id)

        self.report_extraction(video_id)
        info = self._search_regex(r'var experienceJSON = ({.*?});', webpage, 'json')
        info = json.loads(info)['data']
        video_info = info['programmedContent']['videoPlayer']['mediaDTO']

        return self._extract_video_info(video_info)

    def _get_playlist_info(self, player_key):
        playlist_info = self._download_webpage(self._PLAYLIST_URL_TEMPLATE % player_key,
                                               player_key, 'Downloading playlist information')

        json_data = json.loads(playlist_info)
        if 'videoList' not in json_data:
            raise ExtractorError('Empty playlist')
        playlist_info = json_data['videoList']
        videos = [self._extract_video_info(video_info) for video_info in playlist_info['mediaCollectionDTO']['videoDTOs']]

        return self.playlist_result(videos, playlist_id=playlist_info['id'],
                                    playlist_title=playlist_info['mediaCollectionDTO']['displayName'])

    def _extract_video_info(self, video_info):
        info = {
            'id': video_info['id'],
            'title': video_info['displayName'],
            'description': video_info.get('shortDescription'),
            'thumbnail': video_info.get('videoStillURL') or video_info.get('thumbnailURL'),
            'uploader': video_info.get('publisherName'),
        }

        renditions = video_info.get('renditions')
        if renditions:
            renditions = sorted(renditions, key=lambda r: r['size'])
            best_format = renditions[-1]
            info.update({
                'url': best_format['defaultURL'],
                'ext': 'mp4',
            })
        elif video_info.get('FLVFullLengthURL') is not None:
            info.update({
                'url': video_info['FLVFullLengthURL'],
                'ext': 'flv',
            })
        else:
            raise ExtractorError('Unable to extract video url for %s' % info['id'])
        return info
