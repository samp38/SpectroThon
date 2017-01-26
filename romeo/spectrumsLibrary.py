class SpectrumsLibrary(object):
	"""
	Spectrums library provides saved spectrums.
	"""

	def getTaggedSpectrums(self):
		"""
		Returns a list of tagged spectrum objects
		"""
		raise NotImplementedError('Subclasses must implement getTaggedSpectrums')

	def save(self, taggedSpectrum):
		"""
		Stores a taggedSpectrum to the database
		"""
		raise NotImplementedError('Subclasses must implement save')

	def getAvailableIndiceForSpecie(self, specieKey):
		"""
		Return an unused indice that can be given to a new tagged spectrum with the given specie
		"""
		raise NotImplementedError('Subclasses must implement getAvailableIndiceForSpecie')
