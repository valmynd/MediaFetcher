from collections import OrderedDict
from PyQt5.QtCore import *
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
		("DownloadProcesses", "Download Processes:"),
		("ExtractionProcesses", "Extraction Processes:"),
	))

	def __init__(self, qsettings_object):
		QAbstractTableModel.__init__(self)
		self.settings = qsettings_object
		self._keys = list(self._entries.keys())
		self.initDefaults()

	def initDefaults(self):
		keys = self.settings.childKeys()
		folder = self.settings.value("DefaultDownloadFolder")
		if folder is None or not os.access(folder, os.W_OK):
			self.settings.setValue("DefaultDownloadFolder", os.path.join(QDir.homePath(), "Downloads"))
		if "DefaultFileName" not in keys:
			self.settings.setValue("DefaultFileName", "%Title%.%extension%")
		if "DownloadSpeedLimit" not in keys:
			self.settings.setValue("DownloadSpeedLimit", 0)
		if "PoolUpdateFrequency" not in keys:
			self.settings.setValue("PoolUpdateFrequency", 1)
		if "DownloadProcesses" not in keys:
			self.settings.setValue("DownloadProcesses", 4)
		if "ExtractionProcesses" not in keys:
			self.settings.setValue("ExtractionProcesses", 2)

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
			return self.settings.value(key)

	def setData(self, index, value, role):
		if role != Qt.EditRole:
			return False
		num_col = index.column()
		key = self._keys[num_col]
		# print(key, value) # TODO: apply changes on the models!!!
		self.settings.setValue(key, value)
		self.dataChanged.emit(index, index)
		return True
