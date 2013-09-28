from PySide.QtCore import *
from PySide.QtGui import *
from .infoview import InfoBoxDialog
import json

__author__ = "C. Wilhelm"
___license___ = "GPL v3"


class IntuitiveTreeView(QTreeView):
	"""Variant of QTreeView with setStretchFirstSection() method"""

	def __init__(self, parent=None):
		QTreeView.__init__(self, parent)
		self.hv = self.header()
		self.hv.installEventFilter(self)
		self.hv.sectionResized.connect(self.sectionWasResized)
		self.setStretchLastSection = self.hv.setStretchLastSection
		self.setStretchLastSection(False)
		self._stretch_first = False

	def eventFilter(self, obj, event):
		# http://qt-project.org/doc/qt-5.0/qtcore/qobject.html#installEventFilter
		if self._stretch_first and obj == self.hv and event.type() == QEvent.Resize:
			self.stretchSection()
			return True
		return QObject.eventFilter(self, obj, event)

	def sectionWasResized(self, logicalIndex, oldSize, newSize):
		if not self._stretch_first or 0 in (oldSize, newSize):
			return
		v_this = self.hv.visualIndex(logicalIndex)
		l_next = self.hv.logicalIndex(v_this + 1)
		self.stretchSection(l_next)

	def stretchSection(self, logicalIndex=None):
		if logicalIndex is None:
			logicalIndex = self.hv.logicalIndexAt(0)
		unused_width = self.hv.size().width() - self.hv.length()
		new_width = self.hv.sectionSize(logicalIndex) + unused_width
		if new_width > self.hv.minimumSectionSize():
			oldState = self.hv.blockSignals(True)
			self.hv.resizeSection(logicalIndex, new_width)
			self.hv.blockSignals(oldState)

	def setStretchFirstSection(self, stretch_first=True):
		# quasi-counterpart for setStretchLastSection() (which is actually part of QHeaderView)
		# subclassing QHeaderView is no option here, as the QTreeView defaults would be lost!
		self._stretch_first = stretch_first

	def setNoStretch(self):
		self.setStretchFirstSection(False)
		self.setStretchLastSection(False)


class QueueTreeView(IntuitiveTreeView):
	_ignored_columns = []  # columns that would break the table layout, e.g. multiline descriptions, thumbnails
	_visible_columns = []  # columns that weren't deselected by the user or by default NOTE: order is relevant!
	_always_visible_column = 'Filename'

	def __init__(self, main_window, qsettings_object, model):
		IntuitiveTreeView.__init__(self, main_window)
		self.setModel(model)
		self.settings = qsettings_object
		self.loadSettings()
		main_window.aboutToQuit.connect(self.writeSettings)

		# Configure Header
		self.hv.setContextMenuPolicy(Qt.CustomContextMenu)
		self.hv.customContextMenuRequested.connect(self.chooseColumns)
		self.hv.setMaximumHeight(21)
		self.setStretchFirstSection(True)

		# Setup Context Menu
		self.setContextMenuPolicy(Qt.CustomContextMenu)
		self.customContextMenuRequested.connect(self.showContextMenu)
		self.infobox = InfoBoxDialog(self, self.model())

		# Other basic configuration
		#self.setAlternatingRowColors(True) # Somehow doesn't work too well when Delegates are used
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
				j = self.hv.visualIndex(i)
				visible_columns[j] = column_title
		visible_columns = list(filter(None, visible_columns))  # remove None Values
		self.settings.setValue("VisibleColumns", json.dumps(visible_columns))
		self.settings.endGroup()

	def initColumns(self, visible_columns=[]):
		self.hv.blockSignals(True)
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
			if column_title != self._always_visible_column:
				self.columnMenu.addAction(qa)
		self.columnMenu.addSeparator()
		self.columnMenu.addAction(QAction("Reset Defaults", self, triggered=self.resetColumnDefaults))
		for i, column_title in enumerate(visible_columns):
			j = self.model()._columns.index(column_title)
			k = self.hv.logicalIndex(j)
			self.hv.swapSections(k, i)
		self.hv.blockSignals(False)

	def resetColumnDefaults(self):
		self.hv.blockSignals(True)
		for i, column_title in enumerate(self.model()._columns):
			k = self.hv.logicalIndex(i)
			self.hv.resizeSection(k, self.hv.defaultSectionSize())
			self.hv.swapSections(k, i)
		self.hv.blockSignals(False)
		self.initColumns(self._visible_columns)
		self.stretchSection()

	def toggleColumn(self, column_title=None):
		if column_title is None:
			column_title = self.sender().text()
		i = self.model()._columns.index(column_title)
		self.setColumnHidden(i, not self.isColumnHidden(i))
		self.stretchSection()

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
