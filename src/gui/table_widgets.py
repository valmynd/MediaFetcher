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

		# Basic Configuration
		self.setAlternatingRowColors(True)
		#self.setDragDropMode(self.InternalMove)
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

	def getSelectedRows(self):
		return [object.row() for object in self.selectionModel().selectedRows()]

class ClipBoardTableWidget(_BaseTableWidget):
	_header_titles = ['Title', 'Host', 'Status', 'Format', 'Quality']

	def __init__(self, download_widget):
		_BaseTableWidget.__init__(self)
		assert isinstance(download_widget, DownloadTableWidget)
		self.download_widget = download_widget
		self.clipboard_items = []
		self.setContextMenuPolicy(Qt.CustomContextMenu)
		self.customContextMenuRequested.connect(self.showContextMenu)
		self.clipBoardMenu = QMenu()
		download_all = QAction('Download All', self, triggered=self.downloadAll)
		download_selected = QAction('Download Selected', self, triggered=self.downloadSelected)
		info_action = QAction('Info', self, triggered=self.download_widget.showInfo)
		#download_all.setIcon(QIcon.fromTheme("list-add"))
		self.clipBoardMenu.addAction(download_all)
		self.clipBoardMenu.addAction(download_selected)
		self.clipBoardMenu.addAction(info_action)

	def showContextMenu(self, pos):
		globalPos = self.mapToGlobal(pos)
		selectedItem = self.clipBoardMenu.exec_(globalPos)

	def downloadAll(self):
		alert('downloadAll triggered')

	def downloadSelected(self):
		for num_row in self.getSelectedRows():
			self.download_widget.addItem(self.getDownloadItem(num_row))
			self.removeRow(num_row)

	def _add_row(self, title='', host='', status='', format_options=[], quality_options=[]):
		r = _BaseTableWidget._add_row(self, title, host, status)
		format_combobox = QComboBox()
		quality_combobox = QComboBox()
		#quality_combobox.setStyleSheet('border:0')
		for option in format_options:
			format_combobox.addItem(option)
		for option in quality_options:
			quality_combobox.addItem(option)
		format_combobox.setDisabled(len(format_options) == 1)
		quality_combobox.setDisabled(len(quality_options) == 1)
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
		self.clipboard_items.append(item)
		self._add_row(item.title, item.host, 'Avaiable', item.getExtensions(), item.getDefaultQualityOptions())

	def setFormat(self, num_row, new_format):
		quality_combobox = self.cellWidget(num_row, 4)
		quality_combobox.clear()
		for option in self.clipboard_items[num_row].getQualityOptions(new_format):
			quality_combobox.addItem(option)

	def getDownloadItem(self, num_row):
		item = self.clipboard_items[num_row].getDownloadItem(self.getFormat(num_row), self.getQuality(num_row))
		item.filename = self.getTitle(num_row)
		return item

class DownloadTableWidget(_BaseTableWidget):
	_header_titles = ['Filename', 'Host', 'Status', 'Progress']

	def __init__(self):
		_BaseTableWidget.__init__(self)
		self.download_items = []
		self.setContextMenuPolicy(Qt.CustomContextMenu)
		self.customContextMenuRequested.connect(self.showContextMenu)
		self.downloadMenu = QMenu()
		info_action = QAction('Info', self, triggered=self.showInfo)
		self.downloadMenu.addAction(info_action)

	def showContextMenu(self, pos):
		globalPos = self.mapToGlobal(pos)
		selectedItem = self.downloadMenu.exec_(globalPos)

	def showInfo(self):
		for num_row in self.getSelectedRows():
			download_item = self.download_items[num_row]
			clipboard_item = download_item.clipboard_item
			title_label = QLineEdit(clipboard_item.title)
			description_label = QTextEdit(clipboard_item.description)
			description_label.setReadOnly(True)
			title_label.setReadOnly(True)
			thumbnail_label = QLabel()
			local_thumbnail = clipboard_item.getThumbnail()
			if local_thumbnail:
				thumbnail_label.setPixmap(QPixmap(local_thumbnail))
			else:
				thumbnail_label.setText("None")
			dialog = QDialog()
			layout = QFormLayout()
			layout.addRow(QLabel("Title:"), title_label)
			layout.addRow(QLabel("Description:"), description_label)
			layout.addRow(QLabel("Thumbnail:"), thumbnail_label)
			#layout.addRow(QLabel("Subtitles:"), QLabel(str(clipboard_item.subtitles)))
			#layout.addRow(QLabel("Quality:"), QLabel(download_item))
			dialog.setLayout(layout)
			dialog.exec_()

	def _add_row(self, filename='', host='', status='', progress=0):
		r = _BaseTableWidget._add_row(self, filename, host, status)
		progress_widget = QProgressBar()
		progress_widget.setValue(progress)
		self.setCellWidget(r, 3, progress_widget)
		return r

	def getProgress(self, num_row):
		return self.cellWidget(num_row, 3).value()

	def addItem(self, item):
		assert isinstance(item, DownloadItem)
		self.download_items.append(item)
		self._add_row(item.filename, item.clipboard_item.host, 'Avaiable', 0)