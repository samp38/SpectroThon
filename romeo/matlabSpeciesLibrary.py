import glob
import os
import sys
import scipy.io as sio
sys.path.insert(0, os.path.abspath('.'))
from speciesLibrary import SpeciesLibrary
from specie import Specie


class MatlabSpeciesLibrary(SpeciesLibrary):
	"""
	Matlab formatted Library of species
	"""
	def __init__(self, directory):
		try:
			os.makedirs(directory)
		except OSError:
			pass
		self.directory = directory
		self.speciesByKey = {}
		for fileName in glob.glob(directory+"/*.mat"):
			matlabData = sio.loadmat(fileName)
			key = os.path.splitext(os.path.split(fileName)[1])[0]
			self.speciesByKey[key] = Specie(''.join(matlabData['nature']), key, ''.join(matlabData['concentration']))
	
	
	def getSpeciesByKey(self):
		"""
		@inherit documentation
		"""
		return self.speciesByKey
		
	def addSpecie(self, specie):
		"""
		@inherit documentation
		"""
		self.speciesByKey[specie.key] = specie
		sio.savemat(self.directory + '/' +  specie.key + '.mat', {'nature':specie.name, 'concentration':specie.concentration})