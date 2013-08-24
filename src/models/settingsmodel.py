from PySide.QtCore import *


class SettingsModel(QAbstractTableModel):
	"""
	Model for those items in a QSettings object, that are used in the Preferences Dialog.
	This models sole purpose is to be able to use QDataWidgetMapper!
	For internal purposes, the QSettings object should be used directly, instead.
	"""

	# note: by the inifile "standards", there must be no whitespaces in keys!
	_keys = ["DownloadFolder"]

	def __init__(self, qsettings_object):
		QAbstractTableModel.__init__(self)
		self.settings = qsettings_object

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
		self.settings.setValue(key, value)
		self.dataChanged.emit(index, index)
		return True