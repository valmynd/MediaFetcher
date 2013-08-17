from PySide.QtCore import *
from PySide.QtGui import *


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


class QueueTreeView(QTreeView):
	_ignored_columns = [] # columns that would break the table layout, e.g. multiline descriptions, thumbnails

	def __init__(self, model):
		QTreeView.__init__(self)
		self.setModel(model)

		# Configure Header
		self.header().setContextMenuPolicy(Qt.CustomContextMenu)
		self.header().customContextMenuRequested.connect(self.chooseColumns)
		self.columnMenu = QMenu()
		for i, column_title in enumerate(model._columns):
			if column_title in self._ignored_columns:
				self.setColumnHidden(i, True)
				continue
			qa = QAction(column_title, self, checkable=True, checked=True, triggered=self.toggleColumn)
			self.columnMenu.addAction(qa)

		# Setup Context Menu
		self.setContextMenuPolicy(Qt.CustomContextMenu)
		self.customContextMenuRequested.connect(self.showContextMenu)

		# Other basic configuration
		#self.setAlternatingRowColors(True) # Somehow doesn't work too well when Delegates are used
		self.header().setMaximumHeight(21)
		self.setSelectionBehavior(QAbstractItemView.SelectRows)
		self.setSelectionMode(QAbstractItemView.ExtendedSelection)

	def removeSelected(self):
		self.model().removeScatteredRows(self.selectionModel().selectedRows())

	def removeAll(self):
		self.model().removeAll()

	def toggleColumn(self):
		column_title = self.sender().text()
		i = self.model()._columns.index(column_title)
		self.setColumnHidden(i, not self.isColumnHidden(i))

	def chooseColumns(self, pos):
		globalPos = self.mapToGlobal(pos)
		self.columnMenu.exec_(globalPos)

	def showContextMenu(self, pos):
		raise NotImplementedError

	def updateProgress(self):
		pass
