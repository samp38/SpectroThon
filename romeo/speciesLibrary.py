class SpeciesLibrary(object):
	"""
	Represents a library of species
	"""
	def addSpecie(self, specie):
		"""
		Add a specie in the species Library
		"""
		raise NotImplementedError('Subclasses must implement addSpecie')

	def getSpeciesByKey(self):
		"""
		Return a dictionnary (by key) of all the species in the Library
		"""
		raise NotImplementedError('Subclasses must implement getSpeciesByKey')
