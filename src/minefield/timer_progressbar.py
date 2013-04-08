import sys

from PySide.QtGui import *
from PySide.QtCore import *

class myProgressBar(QProgressBar):
	def __init__(self):
		QProgressBar.__init__(self)
		self.setValue(20)
	def increaseValue(self):
		self.setValue(self.value() + 20)

if __name__ == '__main__':
	app = QApplication(sys.argv)
	progressBar = myProgressBar()

	#Resize width and height
	progressBar.resize(250, 50)
	progressBar.setWindowTitle('PyQt QProgressBar Set Value Example')

	timer = QTimer()
	timer.timeout.connect(progressBar.increaseValue)
	timer.start(4000)

	progressBar.show()
	sys.exit(app.exec_())