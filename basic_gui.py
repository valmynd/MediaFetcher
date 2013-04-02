___license___ = "GPL v3"
from PySide.QtCore import *
from PySide.QtGui import *


class MainWindow(QMainWindow):
	def __init__(self):
		QMainWindow.__init__(self)
		self.createActions()
		self.createMenus()
		self.createToolBars()
		self.createInitialTabs()
		self.setWindowTitle("Media Fetcher")
		self.resize(600, 400)
		self.statusBar()
		# monitor Clipboard
		QObject.connect(QApplication.clipboard(), SIGNAL("dataChanged()"), self,
							   SLOT("clipBoardChanged()"))

	@Slot()
	def clipBoardChanged(self):
		if not QApplication.clipboard().mimeData().hasText(): return
		text = QApplication.clipboard().text()
		if '//' in text: # contains URL
			QMessageBox.information(None, "ClipBoard", text);


	def open(self):
		fileName = QFileDialog.getOpenFileName(self, "Open File", QDir.currentPath())
		if fileName:
			pass

	def about(self):
		QMessageBox.about(self, "About Media Fetcher", "Text")

	def toggleStatusBar(self):
		self.statusBar().show() if self.statusBar().isHidden() else self.statusBar().hide()

	def createActions(self):
		self.openAction = QAction("&Open...", self, shortcut="Ctrl+O", triggered=self.open)
		self.startAction = QAction("&Start All", self, triggered=self.open)
		self.pauseAction = QAction("&Pause All", self, triggered=self.open)
		self.exitAction = QAction("E&xit", self, shortcut="Ctrl+Q", triggered=self.close)
		self.toggleStatusBarAction = QAction("Statusbar", self, checkable=True, checked=True,
												   triggered=self.toggleStatusBar)
		self.settingsAction = QAction("Prefere&nces", self, triggered=self.open)
		self.aboutAction = QAction("About", self, triggered=self.about)
		self.searchAction = QAction("Search", self, triggered=self.about)

		self.openAction.setIcon(QIcon.fromTheme("folder-open"))
		self.startAction.setIcon(QIcon.fromTheme("media-playback-start"))
		self.pauseAction.setIcon(QIcon.fromTheme("media-playback-pause"))
		self.settingsAction.setIcon(QIcon.fromTheme("emblem-system"))
		self.exitAction.setIcon(QIcon.fromTheme("application-exit"))
		self.searchAction.setIcon(QIcon.fromTheme("system-search"))
		self.exitAction.setStatusTip('Exit application')

	def createMenus(self):
		self.fileMenu = QMenu("&File", self)
		self.fileMenu.addAction(self.openAction)
		self.fileMenu.addSeparator()
		self.fileMenu.addAction(self.startAction)
		self.fileMenu.addAction(self.pauseAction)
		self.fileMenu.addSeparator()
		self.fileMenu.addAction(self.exitAction)

		self.editMenu = QMenu("&Edit", self)
		self.editMenu.addAction(self.settingsAction)

		self.viewMenu = QMenu("&View", self)
		self.viewMenu.addAction(self.toggleStatusBarAction)

		self.helpMenu = QMenu("&Help", self)
		self.helpMenu.addAction(self.aboutAction)

		self.menuBar().addMenu(self.fileMenu)
		self.menuBar().addMenu(self.editMenu)
		self.menuBar().addMenu(self.viewMenu)
		self.menuBar().addMenu(self.helpMenu)

	def createToolBars(self):
		# http://aseigo.blogspot.de/2006/08/sweep-sweep-sweep-ui-floor.html
		self.searchBar = QLineEdit()
		self.toolBar = self.addToolBar("Search")
		self.toolBar.addAction(self.openAction)
		self.toolBar.addWidget(self.searchBar)
		self.toolBar.addAction(self.searchAction)
		#self.toolBar.addAction(self.startAction)
		self.toolBar.addAction(self.pauseAction)
		self.toolBar.addAction(self.settingsAction)
		self.toolBar.setMovable(False)
		self.searchAction.setDisabled(True)
		self.pauseAction.setDisabled(True) # QPushButton !

	def createPixmapLabel(self):
		label = QLabel()
		label.setEnabled(False)
		label.setAlignment(Qt.AlignCenter)
		label.setFrameShape(QFrame.Box)
		label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		label.setBackgroundRole(QPalette.Base)
		label.setAutoFillBackground(True)
		label.setMinimumSize(60, 60)
		return label

	def createInitialTabs(self):
		self.tabBar = QTabWidget()
		self.setCentralWidget(self.tabBar)

		# Downloads Tab
		#vbox.addWidget(item)
		#btn = self.createPixmapLabel()
		#grid.addWidget(btn)
		list = QTableWidget()
		item = QWidget()
		item.setLayout(QGridLayout())
		item.setMaximumHeight(100)

		self.tabBar.addTab(list, "Downloads")

		# Clipboard Tab
		self.clipBoardList = QTableWidget()
		self.clipBoardList.setColumnCount(3)
		self.clipBoardList.setRowCount(3)
		self.clipBoardList.setAlternatingRowColors(True)
		self.clipBoardList.setDragDropMode(self.clipBoardList.InternalMove)
		self.clipBoardList.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		self.clipBoardList.setHorizontalHeaderLabels(["Title", "Host", "Quality"])
		self.clipBoardList.horizontalHeader().setResizeMode(0, QHeaderView.Stretch)
		self.clipBoardList.setSelectionBehavior(QAbstractItemView.SelectRows)
		self.clipBoardList.verticalHeader().setDefaultSectionSize(19)
		self.clipBoardList.verticalHeader().hide()
		example = QTableWidgetItem("test")

		self.clipBoardList.setItem(0, 0, example)

		self.tabBar.addTab(self.clipBoardList, "Clipboard")


if __name__ == '__main__':
	import sys

	app = QApplication(sys.argv)
	main_window = MainWindow()
	main_window.show()
	sys.exit(app.exec_())
