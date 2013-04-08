import sys
from PySide import QtCore, QtGui
from PySide.phonon import Phonon
app = QtGui.QApplication(sys.argv)
vp = Phonon.VideoPlayer()
media = Phonon.MediaSource('file:///home/rrae/Music/a-tokyo_dusk-sour.mp3')
vp.load(media)
vp.play()
vp.show()
sys.exit(app.exec_())

