import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from tag import Tag

class Specie(Tag):
	"""
	Represents a chemical specie
	"""
	def __init__(self, name, key, concentration):
		Tag.__init__(self, name, key)
		self.concentration = concentration
		