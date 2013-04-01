## before executing this script, delete everything except this file
touch __init__.py
# http://rg3.github.com/youtube-dl/
git clone https://github.com/rg3/youtube-dl/
mv youtube-dl/youtube_dl .
rm -rf youtube-dl
# http://wiki.videolan.org/Python_bindings
git clone git://git.videolan.org/vlc/bindings/python.git
mv python vlc_py
rm vlc_py/*
rm -rf vlc_py/.git
touch vlc_py/__init__.py
touch vlc_py/generated/__init__.py
