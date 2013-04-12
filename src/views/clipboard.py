from views.base import *


class ComboBoxDelegate(QStyledItemDelegate):
	def createEditor(self, parent, option, index):
		combo = QComboBox(parent)
		combo.addItems(['2', '3', '4'])
		combo.setMaximumHeight(self.sizeHint(option, index).height())
		return combo

	def paint(self, painter, option, index):
		QStyledItemDelegate.paint(self, painter, option, index) # takes care of background color
		self.parent().openPersistentEditor(index) # forces the item into "edit" mode


class ClipBoardView(QueueTreeView):
	def __init__(self, clipboard_model):
		QueueTreeView.__init__(self, clipboard_model)
		self.setItemDelegateForColumn(3, ComboBoxDelegate(self))
		self.setItemDelegateForColumn(4, ComboBoxDelegate(self))

		self.clipBoardMenu = QMenu()
		download_all = QAction('Download All', self, triggered=self.downloadAll)
		download_selected = QAction('Download Selected', self, triggered=self.downloadSelected)
		info_action = QAction('Info', self)#, triggered=self.parent_widget.downloadWidget.showInfo)
		self.clipBoardMenu.addAction(download_all)
		self.clipBoardMenu.addAction(download_selected)
		self.clipBoardMenu.addAction(info_action)

	def showContextMenu(self, pos):
		globalPos = self.mapToGlobal(pos)
		selectedItem = self.clipBoardMenu.exec_(globalPos)

	def downloadAll(self):
		pass

	def downloadSelected(self):
		for num_row in self.getSelectedRows():
			self.parent_widget.downloadWidget.addItem(self.getDownloadItem(num_row))
			self.removeRow(num_row)
