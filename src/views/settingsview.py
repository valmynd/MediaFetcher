from PySide.QtCore import *
from PySide.QtGui import *
import json
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


class SettingsWidgetMapper(QDataWidgetMapper):
	def __init__(self, settings_model):
		"""
		create model-driven Widgets that are bound to a SettingsModel
		@param settings_model: models.settingsmodel.SettingsModel
		"""
		QDataWidgetMapper.__init__(self)
		self.settingsModel = settings_model
		self.setModel(settings_model)

	def map(self, input_widget, settings_key):
		"""
		Shortcut for mapping a settings key to a widget suitible for most use-cases

		@param settings_key: QSettings Key (string), e.g. "DefaultDownloadFolder"
		@param input_widget: QWidget that should be responsible for editing
		@return: QLabel object (with default label defined in SettingsModel)
		"""
		num_col = self.settingsModel._keys.index(settings_key)
		label_text = self.settingsModel._entries[settings_key]
		#print(num_col, label_text)
		self.addMapping(input_widget, num_col)
		return QLabel(label_text)


class SettingsDialog(QDialog):
	def __init__(self, main_window, settings_model):
		QDialog.__init__(self, main_window)
		self.setWindowTitle("Preferences")
		self.settingsModel = settings_model
		self.mapper = SettingsWidgetMapper(self.settingsModel)
		self.mapper.setSubmitPolicy(QDataWidgetMapper.ManualSubmit)
		buttonbox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
		buttonbox.accepted.connect(self.submit)
		buttonbox.rejected.connect(self.close)

		layout = QFormLayout()
		self.setLayout(layout)
		self.folderChooser = QFolderChooser(self)
		self.filenameChooser = QLineEdit()
		layout.addRow(self.mapper.map(self.folderChooser, "DefaultDownloadFolder"), self.folderChooser)
		layout.addRow(self.mapper.map(self.filenameChooser, "DefaultFileName"), self.filenameChooser)
		layout.addRow(QLabel())
		layout.addRow(buttonbox)

	def open(self):
		self.mapper.toFirst()
		self.exec_()

	def submit(self):
		if self.folderChooser.checkPermissions(self.folderChooser.text()):
			self.mapper.submit()
			self.close()


class SpinBoxAction(QWidgetAction):
	def __init__(self, parent, mapper, settings_key):
		QWidgetAction.__init__(self, parent)
		self.settings_key = settings_key
		self.mapper = mapper
		self.widget = self.createMainWidget()
		self.label = self.mapper.map(self.widget, self.settings_key)
		self.setText(self.label.text().replace(':', ''))
		self.createToolTips()
		layout = QHBoxLayout()
		layout.setContentsMargins(0, 0, 0, 0)
		layout.addWidget(self.label)
		layout.addWidget(self.widget)
		self.widget.setFixedHeight(self.label.sizeHint().height() + 5)
		default = QWidget(parent)
		default.setLayout(layout)
		default.setParent(parent)
		self.setDefaultWidget(default)

	def createMainWidget(self):
		if self.settings_key == "PoolUpdateFrequency":
			spinbox = QDoubleSpinBox()
			spinbox.setRange(0.5, 20)
			spinbox.setSingleStep(0.5)
			spinbox.setAccelerated(True)
			spinbox.setDecimals(2)
			spinbox.setSuffix(" s")
			return spinbox
		elif self.settings_key in ("DownloadProcesses", "ExtractionProcesses"):
			spinbox = QSpinBox()
			spinbox.setRange(0, 10)
			spinbox.setSingleStep(1)
			return spinbox
		elif self.settings_key == "DownloadSpeedLimit":
			spinbox = QSpinBox()
			spinbox.setRange(0, 9990)
			spinbox.setSingleStep(10)
			spinbox.setAccelerated(True)
			spinbox.setSuffix(" kb/s")
			return spinbox
		raise Exception("SpinBoxAction: No implementation for %s" % self.settings_key)

	def createToolTips(self):
		if "Limit" in self.settings_key:
			self.label.setToolTip("0 := infinite")
		elif self.settings_key == "PoolUpdateFrequency":
			self.label.setToolTip("Update progress every n seconds. Higher values may slightly enhance battery life.")
		elif self.settings_key == "DownloadProcesses":
			self.label.setToolTip("Number of Download Processes running in the background")
		elif self.settings_key == "ExtractionProcesses":
			self.label.setToolTip("Number of Processes extracting Download Links and Metadata from URLs")


class ConfigurableToolBar(QToolBar):
	seperators_between_actions = False

	def __init__(self, title, main_window):
		QToolBar.__init__(self, title, main_window)
		#self.setStyleSheet("QToolBar { border: 0px; }")
		self.settings = main_window.settings
		main_window.aboutToQuit.connect(self.writeSettings)
		self.setMovable(False)
		self.loadSettings()

	def loadSettings(self):
		self.settings.beginGroup(self.__class__.__name__)
		visible_actions = self.settings.value("VisibleActions", [a.text() for a in self.actions() if a.text()])
		if not isinstance(visible_actions, list):
			visible_actions = json.loads(visible_actions)
		self.visible_actions = visible_actions
		self.settings.endGroup()

	def writeSettings(self):
		self.settings.beginGroup(self.__class__.__name__)
		visible_columns = []
		for action in self.actions():
			if action.text() and action.isVisible():
				visible_columns.append(action.text())
		self.settings.setValue("VisibleActions", json.dumps(visible_columns))
		self.settings.endGroup()

	def contextMenuEvent(self, event):
		menu = QMenu()
		for action in self.actions():
			if action.text():
				qa = QAction(action.text(), self, checkable=True)
				qa.setChecked(action.isVisible())
				qa.toggled.connect(self.toggleAction)
				menu.addAction(qa)
		menu.exec_(event.globalPos())

	def toggleAction(self, is_checked):
		title = self.sender().text()
		lastseperator = None
		for action in self.actions():
			if action.isSeparator():
				lastseperator = action
			elif title == action.text():
				action.setVisible(is_checked)
				if lastseperator is not None:
					lastseperator.setVisible(is_checked)
				return

	def addAction(self, action):
		visible = action.text() in self.visible_actions
		action.setVisible(visible)
		if self.seperators_between_actions:
			self.addSeparator().setVisible(visible)
		QToolBar.addAction(self, action)

class SettingsToolBar(ConfigurableToolBar):
	seperators_between_actions = True

	def __init__(self, main_window, settings_model):
		ConfigurableToolBar.__init__(self, "Statusbar", main_window)
		self.mainWindow = main_window
		self.label = QLabel("Download Speed: 0 kb/s")
		self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		self.setStyleSheet("QToolBar { border: 0px; }")  # somehow, this line fixes the background color

		self.settingsModel = settings_model
		self.mapper = SettingsWidgetMapper(settings_model)
		self.mapper.setSubmitPolicy(QDataWidgetMapper.AutoSubmit)
		self.mapper.toFirst()

		self.addWidget(self.label)
		self.addAction(SpinBoxAction(self, self.mapper, "DownloadSpeedLimit"))
		self.addAction(SpinBoxAction(self, self.mapper, "PoolUpdateFrequency"))
		self.addAction(SpinBoxAction(self, self.mapper, "DownloadProcesses"))
		self.addAction(SpinBoxAction(self, self.mapper, "ExtractionProcesses"))