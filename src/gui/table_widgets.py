___license___ = 'GPL v3'

from PySide.QtCore import *
from PySide.QtGui import *


def alert(text):
	QMessageBox.information(None, 'Alert', str(text))


class _BaseTableWidget(QTableWidget):
	_header_titles = []

	def __init__(self, *args, **kwargs):
		QTableWidget.__init__(self, *args, **kwargs)
		# Basic Configuration
		self.setAlternatingRowColors(True)
		self.setDragDropMode(self.InternalMove)
		self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		self.setSelectionBehavior(QAbstractItemView.SelectRows)
		self.setShowGrid(False)
		# Init Headers
		self.setColumnCount(len(self._header_titles))
		self.setHorizontalHeaderLabels(self._header_titles)

		# Configure Horizontal Header
		#self.horizontalHeader().setStretchLastSection(True)
		#self.horizontalHeader().setResizeMode(QHeaderView.Stretch)
		self.horizontalHeader().setResizeMode(QHeaderView.ResizeToContents)
		self.horizontalHeader().setResizeMode(0, QHeaderView.Stretch)
		self.horizontalHeader().setHighlightSections(False)
		self.horizontalHeader().setContextMenuPolicy(Qt.CustomContextMenu)
		self.horizontalHeader().customContextMenuRequested.connect(self.chooseColummns)
		self.columnMenu = QMenu()
		for column_title in self._header_titles:
			qa = QAction(column_title, self, checkable=True, checked=True, triggered=self.toggleColumn)
			self.columnMenu.addAction(qa)

		# Configure Vertical Header
		self.verticalHeader().setDefaultSectionSize(22)
		self.verticalHeader().hide()

	def toggleColumn(self):
		column_title = self.sender().text()
		i = self._header_titles.index(column_title)
		self.setColumnHidden(i, not self.isColumnHidden(i))

	def chooseColummns(self, pos):
		globalPos = self.mapToGlobal(pos)
		selectedItem = self.columnMenu.exec_(globalPos)

	def getStatus(self, num_row):
		return self.item(num_row, 2).text()

	def getTitle(self, num_row):
		return self.item(num_row, 0).text()

	def getHost(self, num_row):
		return self.item(num_row, 1).text()

	def addRow(self, title, host, status):
		r = self.rowCount()
		self.setRowCount(r + 1)
		title_item = QTableWidgetItem(title)
		host_item = QTableWidgetItem(host)
		host_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
		status_item = QTableWidgetItem(status)
		status_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
		self.setItem(r, 0, title_item)
		self.setItem(r, 1, host_item)
		self.setItem(r, 2, status_item)
		return r


class ClipBoardTableWidget(_BaseTableWidget):
	_header_titles = ['Title', 'Host', 'Status', 'Format', 'Quality']

	def getFormat(self, num_row):
		return self.cellWidget(num_row, 3).currentText()

	def getQuality(self, num_row):
		return self.cellWidget(num_row, 4).currentText()

	def addRow(self, title='', host='', status='', format_options=[], quality_options=[]):
		r = _BaseTableWidget.addRow(self, title, host, status)
		format_combobox = QComboBox()
		quality_combobox = QComboBox()
		#quality_combobox.setStyleSheet('border:0')
		for option in format_options:
			format_combobox.addItem(option)
		for option in quality_options:
			quality_combobox.addItem(option)
		self.setCellWidget(r, 3, format_combobox)
		self.setCellWidget(r, 4, quality_combobox)
		return r

	#def addItem(self, item = {}):
	#	"""currently takes a dict, see MediaExtractor in extractors.py!"""
	#	r = _BaseTableWidget.addRow(self, title, host, status)

class DownloadTableWidget(_BaseTableWidget):
	_header_titles = ['Filename', 'Host', 'Status', 'Progress']

	def getProgress(self, num_row):
		return self.cellWidget(num_row, 3).value()

	def addRow(self, title='', host='', status='', progress=0):
		r = _BaseTableWidget.addRow(self, title, host, status)
		progress_widget = QProgressBar()
		progress_widget.setValue(progress)
		self.setCellWidget(r, 3, progress_widget)
		return r