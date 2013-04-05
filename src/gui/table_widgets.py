___license___ = 'GPL v3'

from PySide.QtCore import *
from PySide.QtGui import *
from lib.items import DownloadItem, ClipBoardItem


def alert(text):
	QMessageBox.information(None, 'Alert', str(text))


class _BaseTableWidget(QTableWidget):
	_header_titles = []

	def __init__(self, *args, **kwargs):
		QTableWidget.__init__(self, *args, **kwargs)
		# mapping title => ClipBoardItem (resp. DownloadItem)
		self.media = []

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
		self.horizontalHeader().customContextMenuRequested.connect(self.chooseColumns)
		self.columnMenu = QMenu()
		for column_title in self._header_titles:
			qa = QAction(column_title, self, checkable=True, checked=True, triggered=self.toggleColumn)
			self.columnMenu.addAction(qa)

		# Configure Vertical Header
		self.verticalHeader().setDefaultSectionSize(22)
		self.verticalHeader().hide()

	def _add_row(self, title, host, status):
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

	def toggleColumn(self):
		column_title = self.sender().text()
		i = self._header_titles.index(column_title)
		self.setColumnHidden(i, not self.isColumnHidden(i))

	def chooseColumns(self, pos):
		globalPos = self.mapToGlobal(pos)
		selectedItem = self.columnMenu.exec_(globalPos)

	def getStatus(self, num_row):
		return self.item(num_row, 2).text()

	def getTitle(self, num_row):
		return self.item(num_row, 0).text()

	def getHost(self, num_row):
		return self.item(num_row, 1).text()


class ClipBoardTableWidget(_BaseTableWidget):
	_header_titles = ['Title', 'Host', 'Status', 'Format', 'Quality']

	#def __init__(self):
	#	_BaseTableWidget.__init__(self)

	def _add_row(self, title='', host='', status='', format_options=[], quality_options=[]):
		r = _BaseTableWidget._add_row(self, title, host, status)
		format_combobox = QComboBox()
		quality_combobox = QComboBox()
		#quality_combobox.setStyleSheet('border:0')
		for option in format_options:
			format_combobox.addItem(option)
		for option in quality_options:
			quality_combobox.addItem(option)
		self.setCellWidget(r, 3, format_combobox)
		self.setCellWidget(r, 4, quality_combobox)
		format_combobox.currentIndexChanged['QString'].connect(lambda value, func=self.setFormat: func(r, value))
		return r

	def getFormat(self, num_row):
		return self.cellWidget(num_row, 3).currentText()

	def getQuality(self, num_row):
		return self.cellWidget(num_row, 4).currentText()

	def addItem(self, item):
		assert isinstance(item, ClipBoardItem)
		self.media.append(item)
		self._add_row(item.title, item.host, 'Avaiable', item.getExtensions(), item.getDefaultQualityOptions())

	def setFormat(self, num_row, new_format):
		quality_combobox = self.cellWidget(num_row, 4)
		quality_combobox.clear()
		for option in self.media[num_row].getQualityOptions(new_format):
			quality_combobox.addItem(option)

class DownloadTableWidget(_BaseTableWidget):
	_header_titles = ['Filename', 'Host', 'Status', 'Progress']

	def _add_row(self, title='', host='', status='', progress=0):
		r = _BaseTableWidget._add_row(self, title, host, status)
		progress_widget = QProgressBar()
		progress_widget.setValue(progress)
		self.setCellWidget(r, 3, progress_widget)
		return r

	def getProgress(self, num_row):
		return self.cellWidget(num_row, 3).value()