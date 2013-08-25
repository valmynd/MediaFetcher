from PySide.QtCore import *
from PySide.QtGui import *
from views.infoview import InfoBoxDialog
import json


class QueueTreeView(QTreeView):
	_ignored_columns = []  # columns that would break the table layout, e.g. multiline descriptions, thumbnails
	_visible_columns = []  # columns that weren't deselected by the user or by default NOTE: order is relevant!

	def __init__(self, main_window, qsettings_object, model):
		QTreeView.__init__(self, main_window)
		self.setModel(model)
		self.settings = qsettings_object

		# Configure Header
		self.header().setContextMenuPolicy(Qt.CustomContextMenu)
		self.header().customContextMenuRequested.connect(self.chooseColumns)
		self.loadSettings()
		main_window.closed.connect(self.writeSettings)

		# Setup Context Menu
		self.setContextMenuPolicy(Qt.CustomContextMenu)
		self.customContextMenuRequested.connect(self.showContextMenu)
		self.infobox = InfoBoxDialog(self, self.model())

		# Other basic configuration
		#self.setAlternatingRowColors(True) # Somehow doesn't work too well when Delegates are used
		self.header().setMaximumHeight(21)
		self.setSelectionBehavior(QAbstractItemView.SelectRows)
		self.setSelectionMode(QAbstractItemView.ExtendedSelection)
		self.setDragDropMode(QAbstractItemView.DragDrop)
		self.setDropIndicatorShown(True)

	def loadSettings(self):
		self.settings.beginGroup(self.__class__.__name__)
		visible_columns = self.settings.value("VisibleColumns", self._visible_columns)
		if not isinstance(visible_columns, list):
			visible_columns = json.loads(visible_columns)
		self.initColumns(visible_columns)
		self.settings.endGroup()

	def writeSettings(self):
		self.settings.beginGroup(self.__class__.__name__)
		visible_columns = [None] * len(self.model()._columns)  # intialize to avoid Index Errors
		for i, column_title in enumerate(self.model()._columns):
			if not self.isColumnHidden(i):
				j = self.header().visualIndex(i)
				visible_columns[j] = column_title
		visible_columns = list(filter(None, visible_columns))  # remove None Values
		self.settings.setValue("VisibleColumns", json.dumps(visible_columns))
		self.settings.endGroup()

	def initColumns(self, visible_columns=[]):
		self.columnMenu = QMenu()
		for i, column_title in enumerate(self.model()._columns):
			if column_title in self._ignored_columns:
				self.setColumnHidden(i, True)
				continue
			qa = QAction(column_title, self, checkable=True, triggered=self.toggleColumn)
			if column_title in visible_columns:
				self.setColumnHidden(i, False)
				qa.setChecked(True)
			else:
				self.setColumnHidden(i, True)
				qa.setChecked(False)
			self.columnMenu.addAction(qa)
		self.columnMenu.addSeparator()
		self.columnMenu.addAction(QAction("Reset Defaults", self, triggered=self.resetColumnDefaults))
		for i, column_title in enumerate(visible_columns):
			j = self.model()._columns.index(column_title)
			j = self.header().logicalIndex(j)
			self.header().swapSections(j, i)

	def resetColumnDefaults(self):
		self.initColumns(self._visible_columns)

	def toggleColumn(self, column_title=None):
		if column_title is None:
			column_title = self.sender().text()
		i = self.model()._columns.index(column_title)
		self.setColumnHidden(i, not self.isColumnHidden(i))

	def chooseColumns(self, pos):
		globalPos = self.mapToGlobal(pos)
		self.columnMenu.exec_(globalPos)

	def showInfo(self):
		self.infobox.open_for_selection(self.selectedIndexes()[0])

	def removeSelected(self):
		self.model().removeScatteredRows(self.selectionModel().selectedRows())

	def removeAll(self):
		self.model().removeAll()

	def showContextMenu(self, pos):
		raise NotImplementedError
