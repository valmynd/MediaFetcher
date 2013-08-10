from views.base import *
from models import ElementTreeModel, QueueModel, ClipBoardModel
from multiprocessing import Pool, Queue
from lib.extractors import extract_url


class ComboBoxDelegate(QStyledItemDelegate):
	def __init__(self, parent_widget, model):
		QStyledItemDelegate.__init__(self, parent_widget)
		self._model = model

	def createEditor(self, parent_widget, option, index):
		num_col = index.column()
		element = index.internalPointer()
		if num_col == 3:
			combo = self._model.combo_boxes_format[element]
			#combo.currentIndexChanged.connect(lambda y: self._format_changed(element))
		elif num_col == 4:
			combo = self._model.combo_boxes_quality[element]
			#combo.currentIndexChanged.connect(lambda y: self._quality_changed(element))
		print(combo)
		#combo.setMaximumHeight(self.sizeHint(option, index).height())
		combo.setParent(parent_widget)
		return combo

	def _format_changed(self, element):
		format_combobox = element.format_combobox
		quality_combobox = element.quality_combobox
		selected_extension = format_combobox.currentText()
		element.set("selected", selected_extension)
		# override combobox-items with the quality options avaiable currently selected extension
		quality_combobox.clear()
		quality_options = []
		for option in element.find("format[@extension='"+selected_extension+"']/option"):
			quality_options.append(option.attrib.get("quality"))
		quality_combobox.addItems(quality_options)

	def _quality_changed(self, element):
		selected_extension = element.get("selected")
		print(selected_extension)

	def paint(self, painter, option, index):
		# QItemDelegate.paint() takes care of the background color
		QStyledItemDelegate.paint(self, painter, option, index)
		element = index.internalPointer()
		if element.tag == 'item':
			# force the item into "edit" mode, so the combobox is shown
			self.parent().openPersistentEditor(index)


class ClipBoardView(QueueTreeView):
	def __init__(self):
		#from xml.etree import ElementTree as etree
		#model = ElementTreeModel(etree.parse("models/clipboard_example.xml").getroot())
		#model = QueueModel("models/clipboard_example.xml")
		model = ClipBoardModel("models/clipboard_example.xml")
		QueueTreeView.__init__(self, model)
		self.setItemDelegateForColumn(3, ComboBoxDelegate(self, model))
		self.setItemDelegateForColumn(4, ComboBoxDelegate(self, model))

		self.clipBoardMenu = QMenu()
		download_all = QAction('Download All', self, triggered=self.downloadAll)
		download_selected = QAction('Download Selected', self, triggered=self.downloadSelected)
		info_action = QAction('Info', self, triggered=self.showInfo)
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

	def showInfo(self):
		mapper = QDataWidgetMapper
		mapper.setModel(self.model())
		#mapper.addMapping(mySpinBox, 0)
		#mapper.addMapping(myLineEdit, 1)
		#mapper.addMapping(myCountryChooser, 2)
		mapper.toFirst()

	def updateProgress(self):
		if self.queue.empty(): return
		url, result = self.queue.get()
		if isinstance(result, Exception):
			print(result)
			return
			#element = fromstring(result)
			#self.model().merge(element)