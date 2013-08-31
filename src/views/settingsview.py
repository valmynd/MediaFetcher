from PySide.QtCore import *
from PySide.QtGui import *
from models.settingsmodel import SettingsModel
import os

__author__ = "C. Wilhelm"
___license___ = "GPL v3"


class QFolderChooser(QLineEdit):
	def __init__(self, parent_widget):
		QLineEdit.__init__(self, parent_widget)
		self.button = QToolButton(self)
		self.button.setText("Browse")
		self.button.setCursor(Qt.PointingHandCursor)
		self.button.clicked.connect(self.chooseFolder)
		self.realText = self.text()
		self.setStyleSheet("QLineEdit {background: rgb(220,220,220);}")

	def resizeEvent(self, event):
		self.button.setStyleSheet("QToolButton {margin: 2 0 2 0;}")
		x = self.size().width() - self.button.sizeHint().width()
		self.button.move(x, 0)

	def chooseFolder(self):
		folder = QFileDialog.getExistingDirectory(parent=self, dir=self.text())
		if self.checkPermissions(folder):
			self.setText(folder)

	def checkPermissions(self, folder):
		if not os.access(folder, os.W_OK):
			msg = QMessageBox(self)
			msg.setText("You have no writing priviliges\nfor that folder. Please try again!")
			msg.exec_()
			return False
		return True


class SettingsDialog(QDialog):
	def __init__(self, parent_widget, qsettings_object):
		QDialog.__init__(self, parent_widget)
		settings_model = SettingsModel(qsettings_object)
		self.setWindowTitle("Preferences")
		self.downloadFolderField = QFolderChooser(self)
		self.defaultFileNameField = QLineEdit(self)
		buttonbox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
		buttonbox.accepted.connect(self.submit)
		buttonbox.rejected.connect(self.close)
		layout = QFormLayout()
		layout.addRow(QLabel("Download Folder:"), self.downloadFolderField)
		layout.addRow(QLabel("File Name:"), self.defaultFileNameField)
		layout.addRow(QLabel())
		layout.addRow(buttonbox)
		self.mapper = QDataWidgetMapper(self)
		self.mapper.setModel(settings_model)
		self.mapper.addMapping(self.downloadFolderField, 0)
		self.mapper.addMapping(self.defaultFileNameField, 1)
		self.mapper.setSubmitPolicy(QDataWidgetMapper.ManualSubmit)
		self.setLayout(layout)

	def open(self):
		self.mapper.toFirst()
		self.exec_()

	def submit(self):
		if self.downloadFolderField.checkPermissions(self.downloadFolderField.text()):
			self.mapper.submit()
			self.close()