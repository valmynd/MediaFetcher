## TODO: plugin manager within the GUI
#touch __init__.py
# http://pyload.org/ TODO: python3, paths
#wget -O tmp.zip http://get.pyload.org/get/src/
#unzip tmp.zip
#rm tmp.zip
# http://rg3.github.com/youtube-dl/
wget -O youtube-dl.zip https://github.com/rg3/youtube-dl/archive/master.zip
unzip youtube-dl.zip
#2to3 --output-dir=youtube-dl3 -W -n youtube-dl-master/ # transform into py3
mv youtube-dl-master youtube_dl
rm -rf youtube-dl*
# http://wiki.videolan.org/Python_bindings
#git clone git://git.videolan.org/vlc/bindings/python.git
#mv python vlc_py
#rm vlc_py/*
#rm -rf vlc_py/.git
#touch vlc_py/__init__.py
#touch vlc_py/generated/__init__.py
# http://modeltest-PyQt5.googlecode.com/
# wget http://modeltest-PyQt5.googlecode.com/svn/trunk/ModelTest.py
