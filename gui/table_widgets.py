___license___ = "GPL v3"

from PySide.QtCore import *
from PySide.QtGui import *


def alert(text):
	QMessageBox.information(None, "Alert", text)


class _BaseTableWidget(QTableWidget):
	def __init__(self, *args, **kwargs):
		QTableWidget.__init__(self, *args, **kwargs)
		# Basic Configuration
		self.setAlternatingRowColors(True)
		self.setDragDropMode(self.InternalMove)
		self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		self.setSelectionBehavior(QAbstractItemView.SelectRows)
		self.setShowGrid(False)

	def _initHeaders(self, header_titles=[]):
		self.setColumnCount(len(header_titles))
		self.setHorizontalHeaderLabels(header_titles)
		# Configure Horizontal Header
		#self.horizontalHeader().setStretchLastSection(True)
		#self.horizontalHeader().setResizeMode(QHeaderView.Stretch)
		self.horizontalHeader().setResizeMode(QHeaderView.ResizeToContents)
		self.horizontalHeader().setResizeMode(0, QHeaderView.Stretch)
		self.horizontalHeader().setHighlightSections(False)
		# Configure Vertical Header
		self.verticalHeader().setDefaultSectionSize(22)
		self.verticalHeader().hide()


class ClipBoardTableWidget(_BaseTableWidget):
	def __init__(self):
		_BaseTableWidget.__init__(self)
		self._initHeaders(["Title", "Host", "Quality"])
		self.addRow("test1", "Youtube", ["320p", "720p"])
		#self.addRow("test2", "Youtube", ["320p"])
		#self.addRow("test3", "Youtube", ["320p"])

	def getTitle(self, num_row):
		return self.item(num_row, 0).text()

	def getHost(self, num_row):
		return self.item(num_row, 1).text()

	def getQuality(self, num_row):
		return self.cellWidget(num_row, 2).currentText()

	def addRow(self, title='', host='', quality_options=[]):
		r = self.rowCount()
		self.setRowCount(r + 1)
		title_item = QTableWidgetItem(title)
		host_item = QTableWidgetItem(host)
		host_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
		quality_combobox = QComboBox()
		#quality_combobox.setStyleSheet("border:0")
		for option in quality_options:
			quality_combobox.addItem(option)
		self.setItem(r, 0, title_item)
		self.setItem(r, 1, host_item)
		self.setCellWidget(r, 2, quality_combobox)

class DownloadTableWidget(_BaseTableWidget):
	def __init__(self):
		_BaseTableWidget.__init__(self)
		self._initHeaders(["Title", "Host", "Progress"])
		#self.addRow("test1", "Youtube", ["320p", "720p"])