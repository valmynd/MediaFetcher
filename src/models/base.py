from PySide.QtCore import *
from xml.etree.ElementTree import Element, ElementTree, XMLParser, TreeBuilder, tostring


class ElementTreeModel(QAbstractItemModel):
	"""
	Readonly ItemModel for ElementTree Data structures
	see https://pypi.python.org/pypi/EuroPython2006_PyQt4_Examples/
	also read http://qt-project.org/doc/qt-4.8/itemviews-simpletreemodel.html
	"""
	_columns = ["Tag", "Attributes"]

	def __init__(self, etree_root_element):
		QAbstractItemModel.__init__(self)
		self._root = etree_root_element
		self.layoutChanged.connect(self._rebuild_index)
		self._rebuild_index()

	def _rebuild_index(self):
		self._np = dict((child, (parent, row_index))
		                for parent in self._root.iter()
		                for row_index, child in enumerate(parent))

	def data(self, index, role):
		if not (index.isValid() and role == Qt.DisplayRole): return
		element = index.internalPointer()
		if index.column() == 0:
			return element.tag
		return ";".join("%s=\"%s\"" % (k, v) for k, v in element.items())

	def headerData(self, section, orientation, role):
		if orientation == Qt.Horizontal and role == Qt.DisplayRole:
			return self._columns[section]

	def index(self, row, column, parent=QModelIndex()):
		parent_item = parent.internalPointer() if parent.isValid() else self._root
		return self.createIndex(row, column, parent_item[row])

	def parent(self, index):
		if not index.isValid():
			return QModelIndex()
		parent_item, row_index = self._np[index.internalPointer()]
		if id(parent_item) == id(self._root):
			return QModelIndex()
		return self.createIndex(self._np[parent_item][1], 0, parent_item)

	def rowCount(self, parent):
		item = parent.internalPointer() if parent.isValid() else self._root
		return len(item)

	def columnCount(self, parent):
		return len(self._columns)


class QueueItemElement(Element):
	def _init(self):
		"""by the time the constructor is called, there would be no children yet, thus _init() shall be implemented"""
		pass

	@classmethod
	def _element_factory(cls, tag, attrib, **extra):
		if tag == 'item':
			return cls(tag, attrib, **extra)
		return Element(tag, attrib, **extra)

	@classmethod
	def fromstring(cls, string_containing_xml):
		"""replacement for xml.etree.ElementTree.fromstring() taking care of custom Element initialization"""
		parser = XMLParser(target=TreeBuilder(element_factory=cls._element_factory))
		parser.feed(string_containing_xml)
		root_element = parser.close()
		# the following can be replaced with the in python3.3: element.findall(".//item")
		# ... but it is not too common yet and I don't want hard dependency on lxml
		for item in root_element.iterfind('item'):
			item._init()
		for package in root_element.iterfind('package'):
			for item in package.iterfind('item'):
				item._init()
		return root_element

	@classmethod
	def fromfile(cls, path_to_xml_file):
		"""replacement for xml.etree.ElementTree.parse() taking care of custom Element initialization"""
		with open(path_to_xml_file, 'r') as file:
			string_containing_xml = file.read()
		return cls.fromstring(string_containing_xml)


class QueueModel(ElementTreeModel):
	_element_cls = QueueItemElement

	def __init__(self, path_to_xml_file):
		"""other than ElementTreeModel(), QueueModel() does take a path to an XML file as a parameter"""
		root = self._element_cls.fromfile(path_to_xml_file)
		ElementTreeModel.__init__(self, root)

	def rowCount(self, parent):
		# Only "package" nodes should have children in the view!
		item = parent.internalPointer() if parent.isValid() else self._root
		if item.tag == "item":
			return 0
		return len(item)

	def _rebuild_index(self):
		self._np = dict((child, (parent, row_index))
		                for parent in self._root.iter()
		                for row_index, child in enumerate(parent)
		                if parent.tag in ("clipboard", "package")) # (don't know if that does speedup lookups)