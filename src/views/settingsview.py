from .viewbase import *
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
		# print(num_col, label_text)
		self.addMapping(input_widget, num_col)
		return QLabel(label_text)


class PreferredOrderWidget(QListWidget):
	def __init__(self, options_list):
		QListWidget.__init__(self)
		for option in options_list:
			self.addItem(QListWidgetItem(option))
		self.setDragDropMode(QAbstractItemView.InternalMove)
		self.setMaximumHeight(64)
		self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
		self.setFocusPolicy(Qt.StrongFocus)

	def focusOutEvent(self, event):
		for i in range(self.count()):
			self.item(i).setSelected(False)

	def optionsList(self):
		return [self.item(i).text() for i in range(self.count())]


class SettingsDialog(QDialog):
	def __init__(self, main_window, settings_model):
		QDialog.__init__(self, main_window)
		self.setWindowTitle("Preferences")
		self.settingsModel = settings_model
		self.settings = settings_model.settings
		self.mapper = SettingsWidgetMapper(self.settingsModel)
		self.mapper.setSubmitPolicy(QDataWidgetMapper.ManualSubmit)
		dialoglayout = QVBoxLayout()
		self.setLayout(dialoglayout)

		group = QGroupBox("Download Settings")
		layout = QFormLayout()
		group.setLayout(layout)
		dialoglayout.addWidget(group)
		self.setLayout(layout)
		self.folderChooser = QFolderChooser(self)
		self.folderChooserLabel = self.mapper.map(self.folderChooser, "DefaultDownloadFolder")
		self.filenameChooser = QLineEdit()
		self.filenameChooserLabel = self.mapper.map(self.filenameChooser, "DefaultFileName")
		layout.addRow(self.folderChooserLabel, self.folderChooser)
		layout.addRow(self.filenameChooserLabel, self.filenameChooser)
		# group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
		self.folderChooserLabel.setToolTip("Select a folder where downloaded files may land by default.\n"
																			 "You can set different folders on a per-item basis\n"
																			 "in the Clipboard View: Rightclick on Item → Info")
		self.filenameChooserLabel.setToolTip("Filename Template Conventions:\n"
																				 "%extension% → transform to lowercase (mp4)\n"
																				 "%EXTENSION% → transform to uppercase (MP4)\n"
																				 "%exTenSiOn% or something like that → no transformation\n\n"
																				 "Available Keywords: title, url, host, extension, quality")
		pair = QWidget()
		pairlayout = QHBoxLayout()
		pair.setLayout(pairlayout)
		dialoglayout.addWidget(pair)

		group = QGroupBox("Preferred File Extensions")
		group.setToolTip("Prioritize Format Options by dragging them up or\n"
										 "down in priority relative to each other, so it will\n"
										 "be more likely for the upmost item to be preselected\n"
										 "when adding new Items to the Clipboard Queue.")
		layout = QFormLayout()
		group.setLayout(layout)
		pairlayout.addWidget(group)
		extension_options = self.settings.value("PreferredExtensionOrder", ["mp4", "webm", "mp3", "ogg"])
		if not isinstance(extension_options, list):
			extension_options = json.loads(extension_options)
		self.extensionOrderWidget = PreferredOrderWidget(extension_options)
		layout.addWidget(self.extensionOrderWidget)

		group = QGroupBox("Preferred Quallity Options")
		group.setToolTip("Prioritize Quality Options by dragging them up or\n"
										 "down in priority relative to each other, so it will\n"
										 "be more likely for the upmost item to be preselected\n"
										 "when adding new Items to the Clipboard Queue.\n\n"
										 "Music Files will always be extracted in the highest\n"
										 "available quality. On Youtube, videos with very low\n"
										 "resolutions may also have lower audio bitrates.")
		layout = QFormLayout()
		group.setLayout(layout)
		pairlayout.addWidget(group)
		quality_options = self.settings.value("PreferredQualityOrder", ["720p", "1080p", "480p", "360p"])
		if not isinstance(quality_options, list):
			quality_options = json.loads(quality_options)
		self.qualityOrderWidget = PreferredOrderWidget(quality_options)
		layout.addWidget(self.qualityOrderWidget)

		buttonbox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
		buttonbox.accepted.connect(self.submit)
		buttonbox.rejected.connect(self.close)
		dialoglayout.addWidget(buttonbox)
		self.settings.setValue("PreferredExtensionOrder", json.dumps(extension_options))
		self.settings.setValue("PreferredQualityOrder", json.dumps(quality_options))
		self.resize(450, self.sizeHint().height())

	def open(self):
		self.mapper.toFirst()
		self.exec_()

	def submit(self):
		if self.folderChooser.checkPermissions(self.folderChooser.text()):
			self.mapper.submit()
			extension_options = self.extensionOrderWidget.optionsList()
			quality_options = self.qualityOrderWidget.optionsList()
			self.settings.setValue("PreferredExtensionOrder", json.dumps(extension_options))
			self.settings.setValue("PreferredQualityOrder", json.dumps(quality_options))
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
		# self.setStyleSheet("QToolBar { border: 0px; }")
		self.settings = main_window.settings
		main_window.aboutToQuit.connect(self.writeSettings)
		self.setMovable(False)
		self.loadSettings()

	def loadSettings(self):
		self.settings.beginGroup(self.__class__.__name__)
		self.visible_actions = self.settings.value("VisibleActions", [])
		if not isinstance(self.visible_actions, list):
			self.visible_actions = json.loads(self.visible_actions)
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
		visible = action.text() in self.visible_actions or len(self.visible_actions) == 0
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

		self.addWidget(self.label)
		self.addAction(SpinBoxAction(self, self.mapper, "DownloadSpeedLimit"))
		self.addAction(SpinBoxAction(self, self.mapper, "PoolUpdateFrequency"))
		self.addAction(SpinBoxAction(self, self.mapper, "DownloadProcesses"))
		self.addAction(SpinBoxAction(self, self.mapper, "ExtractionProcesses"))
		self.mapper.toFirst()
