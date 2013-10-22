# coding: utf-8

import re
import json

from .common import InfoExtractor


class TudouIE(InfoExtractor):
    _VALID_URL = r'(?:http://)?(?:www\.)?tudou\.com/(?:listplay|programs|albumplay)/(?:view|(.+?))/(?:([^/]+)|([^/]+))(?:\.html)?'
    _TESTS = [{
        'url': 'http://www.tudou.com/listplay/zzdE77v6Mmo/2xN2duXMxmw.html',
        'file': '159448201.f4v',
        'md5': '140a49ed444bd22f93330985d8475fcb',
        'info_dict': {
            "title": "卡马乔国足开大脚长传冲吊集锦"
        }
    },
    {
        'url': 'http://www.tudou.com/albumplay/TenTw_JgiPM/PzsAs5usU9A.html',
        'file': 'todo.mp4',
        'md5': 'todo.mp4',
        'info_dict': {
            'title': 'todo.mp4',
        },
        'add_ie': ['Youku'],
        'skip': 'Only works from China'
    }]

    def _url_for_id(self, id, quality = None):
        info_url = "http://v2.tudou.com/f?id="+str(id)
        if quality:
            info_url += '&hd' + quality
        webpage = self._download_webpage(info_url, id, "Opening the info webpage")
        final_url = self._html_search_regex('>(.+?)</f>',webpage, 'video url')
        return final_url

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        video_id = mobj.group(2)
        webpage = self._download_webpage(url, video_id)

        m = re.search(r'vcode:\s*[\'"](.+?)[\'"]', webpage)
        if m and m.group(1):
            return {
                '_type': 'url',
                'url': 'youku:' + m.group(1),
                'ie_key': 'Youku'
            }

        title = self._search_regex(
            r",kw:\s*['\"](.+?)[\"']", webpage, 'title')
        thumbnail_url = self._search_regex(
            r",pic:\s*[\"'](.+?)[\"']", webpage, 'thumbnail URL', fatal=False)

        segs_json = self._search_regex(r'segs: \'(.*)\'', webpage, 'segments')
        segments = json.loads(segs_json)
        # It looks like the keys are the arguments that have to be passed as
        # the hd field in the request url, we pick the higher
        quality = sorted(segments.keys())[-1]
        parts = segments[quality]
        result = []
        len_parts = len(parts)
        if len_parts > 1:
            self.to_screen('%s: found %s parts' % (video_id, len_parts))
        for part in parts:
            part_id = part['k']
            final_url = self._url_for_id(part_id, quality)
            ext = (final_url.split('?')[0]).split('.')[-1]
            part_info = {'id': part_id,
                          'url': final_url,
                          'ext': ext,
                          'title': title,
                          'thumbnail': thumbnail_url,
                          }
            result.append(part_info)

        return result
