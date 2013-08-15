from views.viewbase import *
from models import ClipBoardModel


class ComboBoxDelegate(QStyledItemDelegate):
	def __init__(self, parent_widget, model):
		QStyledItemDelegate.__init__(self, parent_widget)
		self._model = model

	def createEditor(self, parent_widget, option, index):
		num_col = index.column()
		element = index.internalPointer()
		if num_col == 3:
			combo = self._model.combo_boxes_format[element]
			combo.currentIndexChanged.connect(lambda y: self._format_changed(element))
		elif num_col == 4:
			combo = self._model.combo_boxes_quality[element]
			combo.currentIndexChanged.connect(lambda y: self._quality_changed(element))
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


class InfoBoxDialog(QDialog):
	def __init__(self, parent_widget, model):
		QDialog.__init__(self, parent_widget)
		self.setWindowTitle("Clipboard Item Description")
		title_field = QLineEdit()
		description_field = QPlainTextEdit()
		#description_field.setReadOnly(True) # wouldn't make sense to edit this (?)
		thumbnail_field = QLabel()
		buttonbox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
		buttonbox.accepted.connect(self.submit)
		buttonbox.rejected.connect(self.close)
		layout = QFormLayout()
		layout.addRow(QLabel("Title:"), title_field)
		layout.addRow(QLabel("Description:"), description_field)
		layout.addRow(QLabel("Thumbnail:"), thumbnail_field)
		layout.addRow(buttonbox)
		self.mapper = QDataWidgetMapper(self)
		self.mapper.setModel(model)
		self.mapper.addMapping(title_field, 0)
		self.mapper.addMapping(description_field, 5)
		self.mapper.setSubmitPolicy(QDataWidgetMapper.ManualSubmit)
		self.setLayout(layout)

	def open_for_selection(self, selected_index):
		self.mapper.setCurrentModelIndex(selected_index)
		self.exec_()

	def submit(self):
		self.mapper.submit()
		self.close()


class ClipBoardView(QueueTreeView):
	_ignored_columns = ['Description']

	def __init__(self, download_view):
		#from xml.etree import ElementTree as etree
		#clipboard_model = ElementTreeModel(etree.parse("models/clipboard_example.xml").getroot())
		#clipboard_model = QueueModel("models/clipboard_example.xml")
		clipboard_model = ClipBoardModel("models/clipboard_example.xml")
		QueueTreeView.__init__(self, clipboard_model)
		self.setItemDelegateForColumn(3, ComboBoxDelegate(self, clipboard_model))
		self.setItemDelegateForColumn(4, ComboBoxDelegate(self, clipboard_model))
		self.download_view = download_view

		self.clipBoardMenu = QMenu()
		download_selected = QAction('Download Selected', self, triggered=self.downloadSelected)
		download_all = QAction('Download All', self, triggered=self.downloadAll)
		remove_selected = QAction('Remove Selected', self, triggered=self.removeSelected)
		remove_all = QAction('Remove All', self, triggered=self.removeAll)
		info_action = QAction('Info', self, triggered=self.showInfo)
		self.clipBoardMenu.addAction(download_selected)
		self.clipBoardMenu.addAction(download_all)
		self.clipBoardMenu.addAction(remove_selected)
		self.clipBoardMenu.addAction(remove_all)
		self.clipBoardMenu.addAction(info_action)
		self.infobox = InfoBoxDialog(self, self.model())

	def showContextMenu(self, pos):
		globalPos = self.mapToGlobal(pos)
		selectedItem = self.clipBoardMenu.exec_(globalPos)

	def downloadAll(self):
		pass

	def downloadSelected(self):
		for index in self.selectedIndexes():
			if index.column() == 0: # would loop through all columns each row
				#self.parent_widget.downloadWidget.addItem(self.getDownloadItem(num_row))
				element = index.internalPointer()
				self.download_view.addClipboardElement(element)
				self.model().removeElementAtIndex(index, element)

	def removeSelected(self):
		for index in self.selectedIndexes():
			if index.column() == 0: # would loop through all columns each row
				self.model().removeElementAtIndex(index)

	def removeAll(self):
		self.model().removeAll()

	def showInfo(self):
		self.infobox.open_for_selection(self.selectedIndexes()[0])

	def addURL(self, url):
		self.model().addURL(url)

	def updateProgress(self):
		return self.model().updateProgress() # forward to ClipBoardModel