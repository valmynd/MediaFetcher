from .poolbase import *

__author__ = "C. Wilhelm"
___license___ = "GPL v3"


class DownloadProcess(QueueProcess):
	def __init__(self, task_queue, result_queue):
		QueueProcess.__init__(self, task_queue, result_queue, function=self.download)

	def download(self, url, path, filename, download_url, player_url):
		# TODO: download_url als identifier instead of URL
		self.Plugins[0](self).download(url, path, filename, download_url, player_url)


class DownloadPool(QueuePool):
	Process = DownloadProcess

	def add_task(self, url, path, filename, download_url, player_url):
		self.task_queue.put([url, path, filename, download_url, player_url])