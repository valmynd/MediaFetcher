import sys
#import subprocess
from PySide.QtGui import QApplication
from PySide.QtWebKit import QWebPage

class Render(QWebPage):
	def __init__(self, url):
		self.app = QApplication(sys.argv)
		QWebPage.__init__(self)
		self.loadFinished.connect(self._on_loadFinished)
		self.mainFrame().load(url)
		self.app.exec_()

	def _on_loadFinished(self, result):
		self.frame = self.mainFrame()
		self.app.quit()

url_page = 'http://www.myspace.com/music/player?sid=25949923&ac=now'
r = Render(url_page)
html = r.frame.toHtml()
#html = open('out.html').read()


def extractStr(token, haystack):
	begin = haystack.find(token) + len(token)
	end = haystack.find('"', begin)
	return haystack[begin:end]


url_swf = extractStr('"PixelPlayerUrl":"', html)
url_stream = extractStr('"streamURL":"', html)
artist = extractStr('"artistName":"', html)
title = extractStr('"songTitle":"', html)
written_filename = "%(artist)s - %(title)s.mp3" % {'artist': artist, 'title': title}

#http://www.myspace.com/bangkokalcohol
# Siam Old School Records
# STAGE CLEAR

#p = subprocess.Popen(['rtmpdump', '-r', url_stream, '-e', '−−swfVfy', '-W', url_swf])#, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#(out, err) = p.communicate()
#print(out)

cmd = 'rtmpdump -r "%(url_stream)s" -f "WIN 10,3,183,19" -W "%(url_swf)s" -p "%(url_page)s" -o %(filename)s' % dict(
	url_stream=url_stream, url_swf=url_swf, url_page=url_page, filename=written_filename)

print(cmd)
