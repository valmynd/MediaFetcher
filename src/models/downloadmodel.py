from models.modelbase import *
from PySide.QtGui import QProgressBar
from multiprocessing import Pool, Queue
from download import download, pool_init
import os


class DownloadModel(QueueModel):
	_columns = ['Filename', 'Host', 'Status', 'Progress', 'Path']

	def __init__(self, path_to_xml_file):
		QueueModel.__init__(self, path_to_xml_file)

		self.queue = Queue()
		self.pool = Pool(processes=4, initializer=pool_init, initargs=(self.queue,))

	def _init_internal_dict(self):
		# this variant of ElementTreeModel has additional dicts to manage:
		self.progress_bars = {}   # progressbar for each item and package
		self.option_elements = {}  # selected option element for easy access
		QueueModel._init_internal_dict(self)

	def _add_to_internal_dict(self, element, parent, num_row):
		QueueModel._add_to_internal_dict(self, element, parent, num_row)
		progressbar = QProgressBar()
		progressbar.setValue(0)
		self.progress_bars[element] = progressbar
		if element.tag == "item":
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

	def flags(self, index):
		flags = QueueModel.flags(self, index)
		if index.column() == 0:
			flags = flags | Qt.ItemIsEditable
		return flags

	def data(self, index, role):
		if index.isValid() and role in (Qt.DisplayRole, Qt.EditRole):
			element = index.internalPointer()
			num_col = index.column()
			if element.tag == 'item':
				if num_col == 0:
					return element.attrib["title"]
				elif num_col == 1:
					return element.attrib.get("host")
				elif num_col == 2:
					return element.attrib.get("status")
				elif num_col == 3:
					path = element.attrib.get("path")
					size = element.attrib.get("size")
					if path is None or size is None or not os.path.exists(path):
						return 0
					realsize = os.path.getsize(path)
					return realsize / size * 100  # percentage
				elif num_col == 4:
					return element.attrib.get("path")
			elif element.tag == 'package':
				if num_col == 0:
					return element.attrib["name"]

	def setData(self, index, value, role):
		if role != Qt.EditRole or value == "":
			return QueueModel.setData(self, index, value, role)
		element = index.internalPointer()
		num_col = index.column()
		if element.tag == 'item':
			if num_col == 0:
				pass
		self.dataChanged.emit(index, index)
		return True

	def updateProgress(self):
		if self.queue.empty():
			return
		pass