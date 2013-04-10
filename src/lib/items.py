from urllib.request import urlopen
from tempfile import mkdtemp
from os import path
import re

thumbnail_path = mkdtemp(prefix='mf', suffix='thumbnails')


class DownloadItem(object):
	def __init__(self, url, location, player_url, filename='undefined', clipboard_item=None):
		self.url = url
		self.location = location
		self.player_url = player_url
		self.filename = filename
		self.clipboard_item = clipboard_item


class ClipBoardItem(object):
	def __init__(self, title, host="", description="", thumbnail=None, subtitles=[]):
		self.thumbnail = thumbnail
		self._thumbnail_local = None
		self.host = host
		self.title = title
		self.description = description
		self.subtitles = subtitles
		self.formats = {}

	def addDownloadOption(self, format="unknown", quality="unknown", url="", location="?", player_url=None):
		if format == 'unknown':
			# ignore 'unknown', maybe have a setting for that somewhere?
			# don't confuse 'unknown' with 'undefined' -> the latter is to be used for sharehosters
			return
		if format not in self.formats:
			self.formats[format] = {}
		self.formats[format][quality] = DownloadItem(url=url, location=location, player_url=player_url,
													 clipboard_item=self)

	def getThumbnail(self):
		if not isinstance(self.thumbnail, str) or '//' not in self.thumbnail:
			return ''
		if self._thumbnail_local is None:
			tmp_filename = re.sub('[^0-9a-zA-Z]+', '', self.thumbnail)
			tmp_file_path = path.join(thumbnail_path, tmp_filename)
			tmp_file = open(tmp_file_path, 'wb')
			tmp_file.write(urlopen(self.thumbnail).read())
			self._thumbnail_local = tmp_file_path
		return self._thumbnail_local

	def getExtensions(self):
		return list(self.formats.keys())

	def getQualityOptions(self, format):
		return self.formats[format]

	def getDefaultQualityOptions(self):
		# TODO: handle defaults somewhere
		if not self.formats: return []
		first_key = self.getExtensions()[0]
		return self.formats[first_key]

	def getDownloadItem(self, format, quality):
		return self.formats[format][quality]


class ExtractedItems(dict):
	def getTitles(self):
		return self.keys()

	def getClipBoardItem(self, title):
		return self[title]