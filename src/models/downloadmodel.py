from models.modelbase import *
from PySide.QtGui import QComboBox
import tempfile
import os
from multiprocessing import Pool, Queue


class DownloadModel(QueueModel):
	_columns = ['Filename', 'Host', 'Status', 'Progress', 'Path']

	def __init__(self, path_to_xml_file):
		QueueModel.__init__(self, path_to_xml_file)

		self.queue = Queue()
		self.pool = Pool(processes=4, initializer=self._pool_init, initargs=(self.queue,))

	def _pool_init(self, queue):
		# Assign a Queue to a Function that will run in background here
		# see http://stackoverflow.com/a/3843313/852994
		#extract_url._queue = queue
		pass

	def _rebuild_index(self):
		# this variant of ElementTreeModel is mutable -> _n must be flushed every time
		self._n = {}
		for parent in self._root.iter():
			if parent.tag in ("clipboard", "package"):
				for row_index, element in enumerate(parent):
					self._n[element] = (parent, row_index)

	def flags(self, index):
		if index.column() == 0:
			return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable
		return Qt.ItemIsEnabled | Qt.ItemIsSelectable

	def data(self, index, role):
		if index.isValid() and role in (Qt.DisplayRole, Qt.EditRole):
			element = index.internalPointer()
			num_col = index.column()
			if element.tag == 'item':
				if num_col == 0:
					return "Filename"

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