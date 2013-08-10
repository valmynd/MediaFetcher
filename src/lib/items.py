from urllib.request import urlopen
from tempfile import mkdtemp
from os import path
import re
from xml.etree.ElementTree import *

#thumbnail_path = mkdtemp(prefix='mf', suffix='thumbnails')


class DownloadItem(object):
	def __init__(self, url, location, player_url, filename='undefined', clipboard_item=None):
		self.url = url
		self.location = location
		self.player_url = player_url
		self.filename = filename
		self.clipboard_item = clipboard_item

	def addDownloadOption(self, format="unknown", quality="unknown", url="", location="?", player_url=None):
		if format == 'unknown':
			# ignore 'unknown', maybe have a setting for that somewhere?
			# don't confuse 'unknown' with 'undefined' -> the latter is to be used for sharehosters
			return
		if format not in self.formats:
			self.formats[format] = {}
		self.formats[format][quality] = DownloadItem(url=url,
																	location=location,
																	player_url=player_url,
																	clipboard_item=self)

	def getThumbnail(self):
		pass

	def getExtensions(self):
		return list(self.formats.keys())

	def getQualityOptions(self, format):
		return self.formats.get(format)

	def getDefaultQualityOptions(self):
		# TODO: handle defaults somewhere
		if not self.formats: return []
		first_key = self.getExtensions()[0]
		return self.formats[first_key]

	def getDownloadItem(self, format, quality):
		return self.formats[format][quality]


def get_all_items(root_element):
	all_items = list(root_element.iterfind('item'))
	for package in root_element.iterfind('package'):
		all_items += list(package.iterfind('item'))
	return all_items


def post_parse(root_element):
	for item in get_all_items(root_element):
		item.formats = {}
		for format in item.iterfind('format'):
			extension = format.attrib["extension"]
			item.formats[extension] = {}
			for option in format.iterfind('option'):
				quality = option.attrib["quality"]
				item.formats[extension][quality] = option


if __name__ == '__main__':
	#from xml.etree.ElementTree import parse, tostring
	root = parse("../models/clipboard_example.xml").getroot()
	post_parse(root)
	for item in get_all_items(root):
		print(item.formats)

		#print(tostring(root, encoding="unicode"))