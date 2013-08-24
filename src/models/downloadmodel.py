from models.modelbase import *
from PySide.QtGui import QProgressBar
from multiprocessing import Pool, Queue
from download import download, pool_init
import os


class DownloadModel(QueueModel):
	def __init__(self, qsettings_object):
		QueueModel.__init__(self, qsettings_object, "downloads.xml")

		self.commandqueue = Queue()  # contains commands such as "abort", "requeue"
		self.resultqueue = Queue()   # contains result tuples as such: (url, status, size_written, remote_size)
		self.pool = Pool(processes=4, initializer=pool_init, initargs=(self.commandqueue, self.resultqueue,))

	def _init_internal_dict(self):
		# this variant of ElementTreeModel has additional dicts to manage:
		self.progress_bars = {}   # progressbar for each item and package
		self.option_elements = {}  # selected option element for easy access
		QueueModel._init_internal_dict(self)

	def _add_to_internal_dict(self, element, parent, num_row):
		QueueModel._add_to_internal_dict(self, element, parent, num_row)
		if element.tag == "item":
			progressbar = QProgressBar()
			progressbar.setValue(0)
			self.progress_bars[element] = progressbar
			selected_extension = element.get("selected")
			if selected_extension is None:
				element.attrib["status"] = "Error: No Extension selected"
				return
			selected_format = element.find("format[@extension='%s']" % selected_extension)
			if selected_format is None:
				element.attrib["status"] = "Error: No Quality selected"
				return
			selected_quality = selected_format.get("selected")
			option = element.find("format[@extension='%s']/option[@quality='%s']" % (selected_extension, selected_quality))
			self.option_elements[element] = option

	def data(self, index, role):
		if index.isValid() and role in (Qt.DisplayRole, Qt.EditRole):
			# handle extension, quality and progress differently here
			element = index.internalPointer()
			num_col = index.column()
			if element.tag == 'item':
				if num_col == 8:
					return element.attrib.get("selected")
				elif num_col == 9:
					# data() is called VERY often, even when the column ain't visible -> avoid xpath queries here
					option = self.option_elements[element]
					return option.attrib.get("quality")
				elif num_col == 10:
					#path = element.attrib.get("path")
					#size = element.attrib.get("size")
					#if path is None or size is None or not os.path.exists(path):
					#	return 0
					#realsize = os.path.getsize(path)
					#return realsize / size * 100  # percentage
					return 0
			return QueueModel.data(self, index, role)

	def start(self):
		for item in self._root.findall("item[@status='Queued']"):
			item.attrib["status"] = "Progressing"  # TODO: self.dataChanged.emit(index, index)
			option = self.option_elements[item]
			self.pool.apply_async(func=download, args=(item.get("url"), item.get("path"), item.get("filename"),
						option.get("download_url"), option.get("download_url")))

	def pause(self):
		pass

	def updateProgress(self):
		if self.resultqueue.empty():
			return
		pass