from PySide.QtCore import *
from PySide.QtGui import *
#from views.settingsview import QFolderChooser

__author__ = "C. Wilhelm"
___license___ = "GPL v3"


class InfoBoxDialog(QDialog):
	def __init__(self, parent_widget, model):
		QDialog.__init__(self, parent_widget)
		self.setWindowTitle("Clipboard Item Description")
		self.titleField = QLineEdit(self)
		self.descriptionField = QPlainTextEdit(self)
		self.descriptionField.setReadOnly(True) # wouldn't make sense to edit this (?)
		self.descriptionField.setFixedHeight(self.titleField.sizeHint().height() * 2)
		self.thumbnailField = QLabel(self)
		self.thumbnailField.setPixmap(QPixmap('../img/thumbnail_placeholder.png'))
		#self.downloadFolderField = QFolderChooser(self)
		self.fileNameField = QLineEdit(self)
		buttonbox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
		buttonbox.accepted.connect(self.submit)
		buttonbox.rejected.connect(self.close)
		layout = QFormLayout()
		layout.addRow(QLabel("Title:"), self.titleField)
		layout.addRow(QLabel("Description:"), self.descriptionField)
		layout.addRow(QLabel("Thumbnail:"), self.thumbnailField)
		#layout.addRow(QLabel("Download Folder:"), self.downloadFolderField)
		layout.addRow(QLabel("File Name:"), self.fileNameField)
		layout.addRow(QLabel())
		layout.addRow(buttonbox)
		self.mapper = QDataWidgetMapper(self)
		self.mapper.setModel(model)
		self.mapper.addMapping(self.titleField, 0)
		self.mapper.addMapping(self.descriptionField, 3)
		#self.mapper.addMapping(self.downloadFolderField, 5)
		self.mapper.addMapping(self.fileNameField, 6)
		self.mapper.setSubmitPolicy(QDataWidgetMapper.ManualSubmit)
		self.setLayout(layout)

	def open_for_selection(self, selected_index):
		self.mapper.setCurrentModelIndex(selected_index)
		self.exec_()

	def submit(self):
		if self.downloadFolderField.checkPermissions(self.downloadFolderField.text()):
			self.mapper.submit()
			self.close()
