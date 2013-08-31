from .viewbase import *
from models.clipboardmodel import ClipBoardModel

__author__ = "C. Wilhelm"
___license___ = "GPL v3"


class ComboBoxDelegate(QStyledItemDelegate):
	def __init__(self, parent_widget, model):
		QStyledItemDelegate.__init__(self, parent_widget)
		self._model = model

	def createEditor(self, parent_widget, option, index):
		num_col = index.column()
		element = index.internalPointer()
		if num_col == 8:
			combo = self._model.combo_boxes_format[element]
			combo.currentIndexChanged.connect(lambda y: self._format_changed(element))
		elif num_col == 9:
			combo = self._model.combo_boxes_quality[element]
			combo.currentIndexChanged.connect(lambda y: self._quality_changed(element))
		else:
			raise Exception("Only Columns 8, 9 are handled by ComboBoxDelegate")
		combo.setMaximumHeight(self.sizeHint(option, index).height())  # workaround for (qt?) bug when editing labels
		combo.setParent(parent_widget)
		return combo

	def _format_changed(self, element):
		format_combobox = self._model.combo_boxes_format[element]
		quality_combobox = self._model.combo_boxes_quality[element]
		selected_extension = format_combobox.currentText()
		element.set("selected", selected_extension)
		# override combobox-items with the quality options avaiable currently selected extension
		quality_combobox.clear()
		for option in element.findall("format[@extension='" + selected_extension + "']/option"):
			quality_combobox.addItem(option.get("quality"))

	def _quality_changed(self, element):
		quality_combobox = self._model.combo_boxes_quality[element]
		selected_extension = element.get("selected", element.find("format").attrib["extension"])
		selected_format = element.find("format[@extension='%s']" % selected_extension)
		selected_quality = quality_combobox.currentText()
		selected_format.attrib["selected"] = selected_quality

	def paint(self, painter, option, index):
		# QItemDelegate.paint() takes care of the background color
		QStyledItemDelegate.paint(self, painter, option, index)
		element = index.internalPointer()
		if element.tag == 'item':
			# force the item into "edit" mode, so the combobox is shown
			self.parent().openPersistentEditor(index)


class ClipBoardView(QueueTreeView):
	_ignored_columns = ['Url', 'Thumbnail', 'Description', 'Progress']
	_visible_columns = ['Title', 'Host', 'Status', 'Extension', 'Quality']  # excluded: ['Path', 'Filename']

	def __init__(self, main_window, settings, download_view):
		QueueTreeView.__init__(self, main_window, settings, ClipBoardModel(main_window, settings))
		self.setItemDelegateForColumn(8, ComboBoxDelegate(self, self.model()))
		self.setItemDelegateForColumn(9, ComboBoxDelegate(self, self.model()))
		self.download_view = download_view

		self.downloadSelectedAction = QAction('Download Selected', self, triggered=self.downloadSelected)
		self.downloadAllAction = QAction('Download All', self, triggered=self.downloadAll)
		self.removeSelectedAction = QAction('Remove Selected', self, triggered=self.removeSelected)
		self.removeAllAction = QAction('Remove All', self, triggered=self.removeAll)
		self.infoAction = QAction('Info', self, triggered=self.showInfo)

	def showContextMenu(self, pos):
		menu = QMenu()
		menu.addAction(self.downloadSelectedAction)
		menu.addAction(self.downloadAllAction)
		menu.addSeparator()
		menu.addAction(self.removeSelectedAction)
		menu.addAction(self.removeAllAction)
		menu.addSeparator()
		menu.addAction(self.infoAction)
		globalPos = self.mapToGlobal(pos)
		menu.exec_(globalPos)

	def downloadAll(self):
		for element in list(self.model()._root):
			if element.attrib.get("status") == "Available":
				element.attrib["status"] = "Queued"
			self.download_view.addClipboardElement(element)
		self.removeAll()

	def downloadSelected(self):
		# selectedRows() returns the indices in the chronology they were selected, which in this case is perfect
		elements = [index.internalPointer() for index in self.selectionModel().selectedRows()]
		self.removeSelected()  # this will detach otherwise problematic parent->child relationships
		for element in elements:  # the element objects were not garbage-collected, as they're still in that list
			if element.attrib.get("status") == "Available":
				element.attrib["status"] = "Queued"
			self.download_view.addClipboardElement(element)

	def addURL(self, url):
		self.model().addURL(url)