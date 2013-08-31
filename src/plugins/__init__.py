import os

filenames = os.listdir(os.path.dirname(os.path.realpath(__file__)))
modules = [f.replace('.py', '') for f in filenames if f.endswith('.py')]

for module in modules:
	if module != '__init__':
		__import__(module, locals(), globals(), level=1)