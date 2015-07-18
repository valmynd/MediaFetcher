import os, sys

# def load_plugins():
pluginfolderpath = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../plugins"))
filenames = os.listdir(pluginfolderpath)
modules = [f.replace('.py', '') for f in filenames if f.endswith('plugin.py')]
print("MODULES:", modules)
for module in modules:
	__import__(module, locals(), globals(), level=1)
