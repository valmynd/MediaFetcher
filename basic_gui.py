#!/usr/bin/env python

___license___ = "GPL v3"

from PySide.QtCore import *
from PySide.QtGui import *
from gui.table_widgets import *


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

	def dummy(self):
		alert(str(self.clipBoardList.getQuality(0)))

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
		self.settingsAction = QAction("Prefere&nces", self, triggered=self.dummy)
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
		self.downLoadList = DownloadTableWidget()
		self.tabBar.addTab(self.downLoadList, "Downloads")

		# Clipboard Tab
		self.clipBoardList = ClipBoardTableWidget()
		self.tabBar.addTab(self.clipBoardList, "Clipboard")
		self.tabBar.setCurrentIndex(1)


if __name__ == '__main__':
	import sys

	app = QApplication(sys.argv)
	main_window = MainWindow()
	main_window.show()
	sys.exit(app.exec_())
