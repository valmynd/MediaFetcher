___license___ = "GPL v3"
from PySide import QtCore, QtGui

class MainWindow(QtGui.QMainWindow):
	def __init__(self):
		QtGui.QMainWindow.__init__(self)
		self.createActions()
		self.createMenus()
		self.createToolBars()
		self.createInitialTabs()
		self.setWindowTitle("Media Fetcher")
		self.resize(600, 400)
		self.statusBar()

	def open(self):
		fileName = QtGui.QFileDialog.getOpenFileName(self, "Open File", QtCore.QDir.currentPath())
		if fileName:
			pass

	def about(self):
		QtGui.QMessageBox.about(self, "About Media Fetcher", "Text")

	def toggleStatusBar(self):
		self.statusBar().show() if self.statusBar().isHidden() else self.statusBar().hide()

	def createActions(self):
		self.openAction = QtGui.QAction("&Open...", self, shortcut="Ctrl+O", triggered=self.open)
		self.startAction = QtGui.QAction("Start All", self, triggered=self.open)
		self.pauseAction = QtGui.QAction("&Pause All", self, triggered=self.open)
		self.exitAction = QtGui.QAction("E&xit", self, shortcut="Ctrl+Q", triggered=self.close)
		self.toggleStatusBarAction = QtGui.QAction("&Statusbar", self, checkable=True, checked=True,
												   triggered=self.toggleStatusBar)
		self.aboutAction = QtGui.QAction("&About", self, triggered=self.about)
		#print(QtGui.QIcon.hasThemeIcon("edit-undo"))
		#self.openAction.setIcon(QtGui.QIcon.fromTheme("edit-undo", QtGui.QIcon("/home/rrae/src/inspirations/pyside-examples/examples/widgets/icons/images/monkey_on_16x16.png")))
		#self.openAction.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
		self.exitAction.setStatusTip('Exit application')

	def createMenus(self):
		self.fileMenu = QtGui.QMenu("&File", self)
		self.fileMenu.addAction(self.openAction)
		self.fileMenu.addSeparator()
		self.fileMenu.addAction(self.startAction)
		self.fileMenu.addAction(self.pauseAction)
		self.fileMenu.addSeparator()
		self.fileMenu.addAction(self.exitAction)

		self.viewMenu = QtGui.QMenu("&View", self)
		self.viewMenu.addAction(self.toggleStatusBarAction)

		self.helpMenu = QtGui.QMenu("&Help", self)
		self.helpMenu.addAction(self.aboutAction)

		self.menuBar().addMenu(self.fileMenu)
		self.menuBar().addMenu(self.viewMenu)
		self.menuBar().addMenu(self.helpMenu)

	def createToolBars(self):
		self.searchBar = QtGui.QLineEdit()
		self.toolBar = self.addToolBar("Search")
		self.toolBar.addAction(self.openAction)
		self.toolBar.addWidget(self.searchBar)
		self.toolBar.addAction(self.startAction)
		self.toolBar.addAction(self.pauseAction)

	def createInitialTabs(self):
		self.tabBar = QtGui.QTabWidget()
		self.setCentralWidget(self.tabBar)
		self.tabBar.addTab(QtGui.QWidget(), "Browser")

if __name__ == '__main__':
	import sys
	app = QtGui.QApplication(sys.argv)
	imageViewer = MainWindow()
	imageViewer.show()
	sys.exit(app.exec_())
