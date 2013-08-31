from xml.etree.ElementTree import Element, tostring

from core.pluginbase import *
from plugins.youtube_dl.YoutubeDL import *


class YoutubeDLPlugin(Plugin):
	implements_extract = True
	implements_download = True

	def __init__(self, process=None):
		Plugin.__init__(self, process)
		jar = compat_cookiejar.CookieJar()
		cookie_processor = compat_urllib_request.HTTPCookieProcessor(jar)
		proxy_handler = compat_urllib_request.ProxyHandler()
		opener = compat_urllib_request.build_opener(proxy_handler, cookie_processor, YoutubeDLHandler())
		compat_urllib_request.install_opener(opener)
		socket.setdefaulttimeout(60)
		ydl = YoutubeDL(dict(format='all', format_limit=None, ignoreerrors=False, listformats=False,
									consoletitle=False, continuedl=True, forcedescription=False, forcefilename=False,
									forceformat=False, forcethumbnail=False, forcetitle=False, forceurl=False,
									logtostderr=False, matchtitle=None, max_downloads=None, nooverwrites=False,
									nopart=False, noprogress=False, password=None, username=None,
									playlistend=-1, playliststart=1, prefer_free_formats=False, quiet=False,
									ratelimit=None, rejecttitle=None, retries=10, simulate=False, skip_download=False,
									subtitleslang=None, subtitlesformat="srt", test=False, updatetime=True,
									usenetrc=False, verbose=True, writedescription=False,
									writeinfojson=True, writesubtitles=False, onlysubtitles=False, allsubtitles=False,
									listssubtitles=False, outtmpl="%(id)s.%(ext)s"))
		ydl.add_default_info_extractors()
		self.ydl = ydl

	def extract(self, url):
		"""
		Extract information from URL using youtube-dl
		http://rg3.github.io/youtube-dl/
		"""
		info = self.ydl.extract_info(url, download=False)

		if info['_type'] == "compat_list":
			# almost all (meta-)data is actually part of the "entries" (redundant)
			assert len(info['entries']) > 0
			item = Element('item', url=url, status="Available",
								title=info['entries'][0]['title'],
								host=info['entries'][0]['extractor'],
								description=str(info['entries'][0].get('description')),
								thumbnail=str(info['entries'][0].get('thumbnail')))
			formats = {}  # <format> Elements by extension
			for entry in info['entries']:
				# extract relevant Download Options
				extension = entry['ext']
				quality = re.sub(r'^[0-9]+\s-\s', '', entry.get('format'))
				optn = Element('option', quality=quality,
									download_url=str(entry.get('url')),
									location=str(entry.get('location')),
									player_url=str(entry.get('player_url')))
				if extension not in formats:
					formats[extension] = Element('format', extension=extension)
					item.append(formats[extension])
				formats[extension].append(optn)
			xml = tostring(item, encoding="unicode")
			self.send_result(task_id=url, result_object=xml, is_ready=True)
		else:
			#package = Element('package', name="Youtube Playlist") # give more meaningful name!
			#package.extend(items.values())
			raise Exception("Type Not Implemented: %s" % info['_type'])

	def download(self, url, path, filename, download_url, player_url):
		fdl = FileDownloader(self.ydl, self.ydl.params)
		info_dict = {
			'url': download_url,
			'player_url': player_url,
			'page_url': url,
			#'play_path': None,
			#'tc_url': None,
			#'urlhandle': None,
			#'user_agent': None,
		}
		fdl.add_progress_hook(lambda d: self.send_result(url, d)) # TODO: handle interrupt
		filepath = os.path.join(path, filename)
		fdl._do_download(filepath, info_dict)