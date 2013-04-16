from views.base import *
from models import ClipBoardModel
from xml.etree.ElementTree import Element, parse, fromstring
from multiprocessing import Pool, Queue
from lib.extractors import extract_url


class ComboBoxDelegate(QStyledItemDelegate):
	def createEditor(self, parent, option, index):
		num_col = index.column()
		element = index.internalPointer()
		if num_col == 3:
			combo = QComboBox(parent)
			combo.addItems(list(element.formats.keys()))
			combo.currentIndexChanged.connect(self._format_changed)
			element.format_combobox = combo # dirty trick, TODO: find better solution
		elif num_col == 4:
			combo = QComboBox(parent)
			# same as above, except here we must know which format is selected
			selected = element.get("selected", element.find("format").attrib["extension"])
			# the following will work with python3.3: element.findall(".//*[@name='webm']")
			combo.addItems(list(element.formats[selected].keys()))
			element.quality_combobox = combo # dirty trick, TODO: find better solution
			combo.currentIndexChanged.connect(self._quality_changed)
		combo.setMaximumHeight(self.sizeHint(option, index).height())
		combo.element = element # needed in _format_changed(), TODO: find better solution
		return combo

	def _format_changed(self, index):
		format_combobox = self.sender()
		element = format_combobox.element
		quality_combobox = element.quality_combobox
		element.set("selected", format_combobox.currentText())
		quality_combobox.clear()
		selected = element.get("selected", element.find("format").attrib["extension"])
		quality_combobox.addItems(list(element.formats[selected].keys()))

	def _quality_changed(self, index):
		pass

	def paint(self, painter, option, index):
		# QItemDelegate.paint() takes care of the background color
		QStyledItemDelegate.paint(self, painter, option, index)
		element = index.internalPointer()
		if element.tag == 'item':
			# force the item into "edit" mode, so the combobox is shown
			self.parent().openPersistentEditor(index)


class ClipBoardView(QueueTreeView):
	def __init__(self):
		#tmp = Element("clipboard")
		tmp = parse("models/clipboard_example.xml").getroot()
		model = ClipBoardModel(tmp)
		QueueTreeView.__init__(self, model)
		self.setItemDelegateForColumn(3, ComboBoxDelegate(self))
		self.setItemDelegateForColumn(4, ComboBoxDelegate(self))

		self.clipBoardMenu = QMenu()
		download_all = QAction('Download All', self, triggered=self.downloadAll)
		download_selected = QAction('Download Selected', self, triggered=self.downloadSelected)
		info_action = QAction('Info', self)#, triggered=self.parent_widget.downloadWidget.showInfo)
		self.clipBoardMenu.addAction(download_all)
		self.clipBoardMenu.addAction(download_selected)
		self.clipBoardMenu.addAction(info_action)

		self.queue = Queue()
		self.pool = Pool(processes=2, initializer=self._pool_init, initargs=(self.queue,))

	def _pool_init(self, queue):
		# Assign a Queue to a Function that will run in background here
		# see http://stackoverflow.com/a/3843313/852994
		extract_url._queue = queue

	def showContextMenu(self, pos):
		globalPos = self.mapToGlobal(pos)
		selectedItem = self.clipBoardMenu.exec_(globalPos)

	def downloadAll(self):
		pass

	def downloadSelected(self):
		for num_row in self.getSelectedRows():
			self.parent_widget.downloadWidget.addItem(self.getDownloadItem(num_row))
			self.removeRow(num_row)

	def addURL(self, url):
		self.pool.apply_async(func=extract_url, args=(url,))

	#temporary_item = ClipBoardItem(title=url, host="", description="", thumbnail=None, subtitles=[])
	#self.addItem(temporary_item, 'Extracting')

	def updateProgress(self):
		if self.queue.empty(): return
		url, result = self.queue.get()
		if isinstance(result, Exception):
			print(result)
			return
		element = fromstring(result)
		self.model().merge(element)