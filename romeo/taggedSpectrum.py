import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from spectrum import Spectrum

class TaggedSpectrum(Spectrum):
	"""
	TaggedSpectrum is a spectrum with a name
	"""
	def __init__(self, points, tag, indice, fileName=None, deviceConfig=None):
		Spectrum.__init__(self, points, fileName, deviceConfig)
		self.tag = tag
		self.indice = indice
		self.deviceConfig = deviceConfig