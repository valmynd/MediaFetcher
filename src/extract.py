from plugins.youtube_dl.YoutubeDL import *
from xml.etree.ElementTree import Element, tostring
import re


def extract_url_using_youtubedl(url):
	"""
	Extract information from URL using youtube-dl
	http://rg3.github.io/youtube-dl/

	As every such function, it returns either an <item> or <package> xml fragment

	The following are common fields for a title:
	title:          Title defined by the Uploader
	host:           is set to the value for 'extractor'
	thumbnail:      Full URL to a video thumbnail image.
	description:    Description defined by the Uploader
	subtitles:      The subtitle file contents (not handled yet)

	The following fields are specific to a certain Format- and Quality Variant
	url:            Final video URL -> becomes 'download_url'
	location:       Only once used by youtube-dl in rbmaradio.py for country of origin -> ignored!
	player_url:     SWF Player URL -> in some cases needed for rtmpdump
	ext:            Video filename extension -> becomes 'extension'
	format:         The video format -> optional, becomes 'quality'
	"""
	ydl = extract_url_using_youtubedl.ydl  # see pool_init()
	info = ydl.extract_info(url, download=False)

	if info['_type'] == "compat_list":
		# almost all (meta-)data is actually part of the "entries" (redundant)
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
		return tostring(item, encoding="unicode")
	else:
		#package = Element('package', name="Youtube Playlist") # give more meaningful name!
		#package.extend(items.values())
		raise Exception("Unexpected Type: %s" % info['_type'])


def pool_init_for_youtubedl(function_to_apply_to):
	# this can be used for both extract_url_using_youtubedl() and download_using_youtubedl()
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
	function_to_apply_to.ydl = ydl


def pool_init(queue_object):
	# Assign a Queue to the Function that will run in background here
	# see http://stackoverflow.com/a/3843313/852994
	extract_url._queue = queue_object
	pool_init_for_youtubedl(extract_url_using_youtubedl)


def extract_url(url):
	"""
	Extract information from URL using a Backend
	Puts data into multiprocessing.Queue Object
	Queue is assigned to this function in pool_init()

	Goal: list of Backends with configurable priorities
	"""
	try:
		xml = extract_url_using_youtubedl(url)
		#raise Exception("Error: Test Error")
		extract_url._queue.put((url, xml))
	except Exception as e:
		print(e)
		extract_url._queue.put((url, e))


if __name__ == '__main__':
	xml = extract_url_using_youtubedl('http://www.youtube.com/watch?v=v776jlfm7vE')
	print(xml)