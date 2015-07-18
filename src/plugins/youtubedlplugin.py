from core.pluginbase import *
from .youtube_dl.YoutubeDL import *
from .youtube_dl.utils import *
from xml.etree.ElementTree import Element, tostring


class YoutubeDLPlugin(Plugin):
	implements_extract = True
	implements_download = True

	def __init__(self, process=None):
		Plugin.__init__(self, process)

	def extract(self, url):
		ydl = YoutubeDL(dict(password=None, username=None, skip_download=True, verbose=False))
		info = ydl.extract_info(url, download=False)
		item = Element('item', url=url, status="Available",
		               title=info.get('title', ''),
		               host=info.get('extractor', ''),
		               description=info.get('description', ''),
		               thumbnail=info.get('thumbnail', ''))
		formats = {}  # <format> Elements by extension
		for f in info.get('formats', []):
			extension = f.get('ext')
			# quality = "%sx%s" % (f.get('width'), f.get('height'))
			quality = re.sub(r'^[0-9]+\s-\s', '', f.get('format', ''))
			optn = Element('option', quality=quality,
			               plugin_specific=f.get('format_id', 'ERROR'))
			if extension not in formats:
				formats[extension] = Element('format', extension=extension)
				item.append(formats[extension])
			formats[extension].append(optn)
		xml = tostring(item, encoding="unicode")
		self.send_result(task_id=url, result_object=xml, is_ready=True)

	def download(self, url, path, filename, download_url, player_url):

		def __hook(d):
			self.send_result(url, d)

		ydl = YoutubeDL(dict(password=None, username=None, format=format, progress_hooks=[__hook],
		                     nopart=True, noprogress=True, ratelimit=None, retries=10, updatetime=True,
		                     subtitleslang=None, subtitlesformat="srt", onlysubtitles=False, allsubtitles=False,
		                     skip_download=False, verbose=False, outtmpl="%(title)s.%(ext)s"))
		ydl.download([url])


def test():
	# try: from plugins.youtubedlplugin import test;test()
	def dummy(*args, **kwargs):
		print(args, kwargs)
	YoutubeDLPlugin.send_result = dummy
	YoutubeDLPlugin().extract("https://www.youtube.com/watch?v=IsBOoY2zvC0")