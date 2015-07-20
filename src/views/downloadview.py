from views.viewbase import *
from models.downloadmodel import DownloadModel
from subprocess import Popen

__author__ = "C. Wilhelm"
___license___ = "GPL v3"


class ProgressBarDelegate(QStyledItemDelegate):
	def __init__(self, parent_widget, model):
		QStyledItemDelegate.__init__(self, parent_widget)
		self._model = model

	def createEditor(self, parent_widget, option, index):
		element = index.internalPointer()
		progressbar = self._model.progress_bars[element]
		progressbar.setMaximumHeight(self.sizeHint(option, index).height())
		progressbar.setParent(parent_widget)
		return progressbar

	def paint(self, painter, option, index):
		QStyledItemDelegate.paint(self, painter, option, index)  # takes care of background color
		element = index.internalPointer()
		if element.tag == 'item':
			self.parent().openPersistentEditor(index)  # forces the item into "edit" mode


class DownloadView(QueueTreeView):
	_ignored_columns = ['Url', 'Thumbnail', 'Description']
	_visible_columns = ['Filename', 'Host', 'Status', 'Progress']  # excluded: ['Title', 'Path', 'Extension', 'Quality']

	def __init__(self, main_window, settings):
		QueueTreeView.__init__(self, main_window, settings, DownloadModel(main_window, settings))
		self.setItemDelegateForColumn(10, ProgressBarDelegate(self, self.model()))

		self.openFolderAction = QAction('Open Folder', self, triggered=self.openFolder)
		self.pauseSelectedAction = QAction('Pause Selected', self, triggered=self.pauseSelected)
		self.resumeSelectedAction = QAction('Resume Selected', self, triggered=self.resumeSelected)
		self.removeSelectedAction = QAction('Remove Selected', self, triggered=self.removeSelected)
		self.removeAllAction = QAction('Remove All', self, triggered=self.removeAll)
		self.infoAction = QAction('Info', self, triggered=self.showInfo)

	def showContextMenu(self, pos):
		menu = QMenu()
		# TODO: grey out certain options, e.g. no "pause" if all selected items are paused
		menu.addAction(self.openFolderAction)  # only if one folder is selected
		menu.addSeparator()
		menu.addAction(self.pauseSelectedAction)
		menu.addAction(self.resumeSelectedAction)
		menu.addSeparator()
		menu.addAction(self.removeSelectedAction)
		menu.addAction(self.removeAllAction)
		menu.addSeparator()
		menu.addAction(self.infoAction)
		globalPos = self.mapToGlobal(pos)
		menu.exec_(globalPos)

	def openFolder(self):
		for element in [index.internalPointer() for index in self.selectionModel().selectedRows()]:
			path = element.get("path")
			QDesktopServices.openUrl(path)

	def pauseSelected(self):
		pass

	def resumeSelected(self):
		pass

	def addClipboardElement(self, element):
		self.model().addElement(element)  # forward to model
