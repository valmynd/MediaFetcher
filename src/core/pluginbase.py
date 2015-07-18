from .clipboardpool import ClipBoardProcess
from .downloadpool import DownloadProcess

__author__ = "C. Wilhelm"
___license___ = "GPL v3"


class PluginMeta(type):
	def __init__(cls, name, bases, attrs):
		if cls.implements_extract:
			ClipBoardProcess.Plugins.append(cls)
		if cls.implements_download:
			DownloadProcess.Plugins.append(cls)
		type.__init__(cls, name, bases, attrs)


class Plugin(object, metaclass=PluginMeta):
	"""
	subclass this and put it into a python file within the plugin directory
	the file name must contain the word "plugin" and must end with ".py"
	check out plugins/youtubedlplugin.py for a working example
	"""
	implements_extract = False
	implements_download = False

	def __init__(self, process):
		"""@param process: QueueProcess object"""
		self._process = process
		self.interrupt = self._process.hard_interrupt

	def send_result(self, task_id, result_object, is_ready=False):
		self._process.send_result(task_id, result_object, is_ready=is_ready)

	def extract(self, url):
		"""
		calls send_result() either with an <item> or <package> xml fragment (string)
		if extraction process takes long time, this method shall check for self.interrupt.is_set() from time to time
		@param url: url (string) to extract information from; used as task_id
		"""
		raise NotImplementedError

	def download(self, url, path, filename, download_url, player_url):
		"""
		calls send_result() with a dictionary containing the following keys: [...]
		an implementation of this method shall check for self.interrupt.is_set() periodically
		"""
		raise NotImplementedError
