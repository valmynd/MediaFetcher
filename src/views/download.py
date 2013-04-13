from views.base import *


class ProgressBarDelegate(QStyledItemDelegate):
	def createEditor(self, parent, option, index):
		progressbar = QProgressBar(parent)
		progressbar.setMaximumHeight(self.sizeHint(option, index).height())
		return progressbar

	def paint(self, painter, option, index):
		QStyledItemDelegate.paint(self, painter, option, index) # takes care of background color
		self.parent().openPersistentEditor(index) # forces the item into "edit" mode


class DownloadView(QueueTreeView):
	def __init__(self, download_model):
		QueueTreeView.__init__(self, download_model)
		self.setItemDelegateForColumn(3, ProgressBarDelegate(self))
		self.setItemDelegateForColumn(4, ProgressBarDelegate(self))
		self.downloadMenu = QMenu()
		info_action = QAction('Info', self, triggered=self.showInfo)
		self.downloadMenu.addAction(info_action)

	def showContextMenu(self, pos):
		globalPos = self.mapToGlobal(pos)
		selectedItem = self.downloadMenu.exec_(globalPos)