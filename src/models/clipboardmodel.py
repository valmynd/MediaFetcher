from PyQt5.QtWidgets import QComboBox

from .modelbase import *
from core.clipboardpool import ClipBoardPool
import json
import re

__author__ = "C. Wilhelm"
___license___ = "GPL v3"


class ClipBoardModel(QueueModel):
	def __init__(self, main_window, qsettings_object):
		QueueModel.__init__(self, main_window, qsettings_object, "clipboard.xml")
		# self.queue = Queue()
		# self.pool = Pool(processes=2, initializer=pool_init, initargs=(self.queue,))
		self.pool = ClipBoardPool(callback=self.handleProgress)
		main_window.aboutToQuit.connect(self.pool.shutdown)

	def _init_internal_dict(self):
		# this variant of ElementTreeModel has additional dicts to manage:
		self.combo_boxes_format = {}  # format (=extension) combobox for each item
		self.combo_boxes_quality = {}  # quality combobox for each item
		QueueModel._init_internal_dict(self)

	def _add_to_internal_dict(self, element, parent, num_row):
		QueueModel._add_to_internal_dict(self, element, parent, num_row)
		if element.tag == "item":
			# each row gets one combobox for the extension and one for the quality options
			format_combobox = QComboBox()  # see ComboBoxDelegate.createEditor()
			quality_combobox = QComboBox()  # see ComboBoxDelegate.createEditor()
			self.combo_boxes_format[element] = format_combobox
			self.combo_boxes_quality[element] = quality_combobox
			selected_extension = self.getSelectedExtension(element)
			selected_quality = self.getSelectedQuality(element, selected_extension)
			for format in element.findall("format"):
				format_combobox.addItem(format.get("extension"))
			for option in element.findall("format[@extension='%s']/option" % selected_extension):
				quality_combobox.addItem(option.get("quality"))
			format_combobox.setCurrentIndex(format_combobox.findText(selected_extension))
			quality_combobox.setCurrentIndex(quality_combobox.findText(selected_quality))

			# setup defaults for path and filename
			if "path" not in element.attrib:
				path = self.settings.value("DefaultDownloadFolder")
				element.attrib["path"] = path
			if "filename" not in element.attrib:
				filename = self.settings.value("DefaultFileName")
				# some of the template-filling will happen when an Item is moved to DownloadModel, as
				# quality and extension will most probably change until then
				mapping = dict(title=element.get("title"), url=element.get("url"), host=element.get("host"))
				element.attrib["filename"] = fill_filename_template(filename, mapping)

	def getSelectedExtension(self, element):
		format_priorities = json.loads(self.settings.value("PreferredExtensionOrder"))
		selected_extension = element.get("selected")
		if selected_extension is None:  # fallback1: get first found item from priority list
			for preferred_extension in format_priorities:
				found = element.find("format[@extension='%s']" % preferred_extension)
				if found is not None:
					selected_extension = found.attrib["extension"]
					break
			if selected_extension is None:  # fallback 2: get first format which got parsed from XML
				selected_extension = element.find("format").attrib["extension"]
			element.attrib["selected"] = selected_extension
		return selected_extension

	def getSelectedQuality(self, element, selected_extension):
		quality_priorities = json.loads(self.settings.value("PreferredQualityOrder"))
		selected_format = element.find("format[@extension='%s']" % selected_extension)
		selected_quality = selected_format.get("selected")
		if selected_quality is None:  # fallback1: get first found item from priority list
			for preferred_quality in quality_priorities:
				found = selected_format.find("option[@quality='%s']" % preferred_quality)
				if found is not None:
					selected_quality = found.attrib["quality"]
					break
			if selected_quality is None:  # fallback 2: get first format which got parsed from XML
				selected_quality = selected_format.find("option").attrib["quality"]
			selected_format.attrib["selected"] = selected_quality
		return selected_quality

	def addURL(self, url):
		""" add URL to queue -> add temporary item that will be replaced when the information is fetched """
		self.addElement(etree.Element('task', url=url, status="Extracting"))
		# self.pool.apply_async(func=extract_url, args=(url,))
		self.pool.add_task(url)

	def handleProgress(self, url, result, failed, finished):
		task = self._root.find("task[@url='%s']" % url)
		parent, num_row = self._n[task]
		if isinstance(result, Exception):
			index = self.createIndex(num_row, 2, task)
			self.setData(index, str(result), Qt.EditRole)
			return
		self.removeRow(num_row)
		element = etree.fromstring(result)
		self.addElement(element)


def fill_filename_template(filename, mapping):
	"""
	Filename Template Conventions:
	%extension% -> transform to lowercase (mp4)
	%EXTENSION% -> transform to uppercase (MP4)
	%Extension%, %ExTenSiOn% or something like that -> no transformation

	@param filename: filename that contains template variables to be replaced
	@param mapping: python dict that maps keys to replacement values
	@return: str
	"""
	for match in re.findall('(?<=%)[A-Za-z]+(?=%)', filename):
		replaced_str = "%" + match + "%"
		if match.lower() in mapping.keys():
			if match.islower():
				filename = filename.replace(replaced_str, mapping[match].lower())
			elif match.isupper():
				filename = filename.replace(replaced_str, mapping[match.lower()].upper())
			else:
				filename = filename.replace(replaced_str, mapping[match.lower()])
	return filename
