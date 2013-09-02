from collections import OrderedDict
from PySide.QtCore import *
import os


class SettingsModel(QAbstractTableModel):
	"""
	Model for those items in a QSettings object, that are used in the Preferences Dialog.
	This models sole purpose is to be able to use QDataWidgetMapper!
	For internal purposes, the QSettings object should be used directly, instead.
	"""

	_entries = OrderedDict((
		("DefaultDownloadFolder", "Default Download Folder:"),
		("DefaultFileName", "Default File Name:"),
		("DownloadSpeedLimit", "Download Speed Limit:"),
		("PoolUpdateFrequency", "Update Interval:"),
		("DownloadProcesses", "Number of Download Processes:"),
		("ExtractionProcesses", "Number of Extraction Processes:"),
	))

	def __init__(self, qsettings_object):
		QAbstractTableModel.__init__(self)
		self.settings = qsettings_object
		self._keys = list(self._entries.keys())
		self.initDefaults()

	def initDefaults(self):
		folder = self.settings.value("DefaultDownloadFolder")
		if folder is None or not os.access(folder, os.W_OK):
			self.settings.setValue("DefaultDownloadFolder", os.path.join(QDir.homePath(), "Downloads"))
		if self.settings.value("DefaultFileName") is None:
			self.settings.setValue("DefaultFileName", "%Title%.%HOST%.%extension%")

	def rowCount(self, parent):
		return 1

	def columnCount(self, parent):
		return len(self._keys)

	def flags(self, index):
		return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

	def data(self, index, role):
		if index.isValid() and role in (Qt.DisplayRole, Qt.EditRole):
			num_col = index.column()
			key = self._keys[num_col]
			print(key, self.settings.value(key))
			return self.settings.value(key)

	def setData(self, index, value, role):
		#print("KHKSFHKS")
		if role != Qt.EditRole:
			return False
		num_col = index.column()
		key = self._keys[num_col]
		self.settings.setValue(key, value)
		self.dataChanged.emit(index, index)
		return True