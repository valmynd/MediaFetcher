___license___ = 'GPL v3'

from PySide.QtCore import *
from PySide.QtGui import *
from multiprocessing import Pool, Queue
from lib.extractors import extract_url

# DEPRECATED!

def alert(text):
	QMessageBox.information(None, 'Alert', str(text))


class _QFormatComboBox(QComboBox):
	def __init__(self, quality_combobox, clipboard_item):
		QComboBox.__init__(self)
		self.quality_combobox = quality_combobox
		self.clipboard_item = clipboard_item


class _QueueTableWidget(QTableWidget):
	_header_titles = []
	_pool_size = 0

	def __init__(self, main_window):
		QTableWidget.__init__(self)
		assert isinstance(main_window, QMainWindow)
		self.parent_widget = main_window

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

		# Every Tab might have a Pool of Background Processes
		if self._pool_size > 0:
			self.queue = Queue()
			self.pool = Pool(processes=self._pool_size, initializer=self._pool_init, initargs=(self.queue,))

	def _pool_init(self, queue):
		# Assign a Queue to a Function that will run in background here
		# see http://stackoverflow.com/a/3843313/852994
		pass

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

	def getRowByFirstColumn(self, content=''):
		widget_items = self.findItems(content, Qt.MatchExactly)
		assert len(widget_items) == 1
		return widget_items[0].row()

	def toggleColumn(self):
		column_title = self.sender().text()
		i = self._header_titles.index(column_title)
		self.setColumnHidden(i, not self.isColumnHidden(i))

	def chooseColumns(self, pos):
		globalPos = self.mapToGlobal(pos)
		selectedItem = self.columnMenu.exec_(globalPos)

	def getSelectedRows(self):
		return [object.row() for object in self.selectionModel().selectedRows()]

	def updateProgress(self):
		pass


class DownloadTableWidget(_QueueTableWidget):
	_header_titles = ['Filename', 'Host', 'Status', 'Progress']

	def __init__(self, main_window):
		_QueueTableWidget.__init__(self, main_window)
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

	def getProgress(self, num_row):
		return self.cellWidget(num_row, 3).value()

	def addItem(self, item):
		#assert isinstance(item, DownloadItem)
		self.download_items.append(item)
		r = self._add_row(item.filename, item.clipboard_item.host, 'Available')
		progress_widget = QProgressBar()
		progress_widget.setValue(0)
		self.setCellWidget(r, 3, progress_widget)