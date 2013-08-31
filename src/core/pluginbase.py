from .poolbase import *

__author__ = "C. Wilhelm"
___license___ = "GPL v3"


class Plugin(object):
	implements_extract = False
	implements_download = False

	def __init__(self, process):
		"""@param process: QueueProcess object"""
		# TODO: register plugin via metaclass
		self._process = process
		self.interrupt = self._process.hard_interrupt
		self.send_result = self._process.send_result

	def extract(self, url):
		"""
		@return: either an <item> or <package> xml fragment (string)
		"""
		raise NotImplementedError

	def download(self, url, path, filename, download_url, player_url):
		"""
		@return: dictionary with the following keys: [...]
		"""
		raise NotImplementedError