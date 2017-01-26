import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from taggedSpectrum import TaggedSpectrum
from spectrum import Spectrum
from spectrumsLibrary import SpectrumsLibrary
import scipy.io as sio
import numpy
import glob
from specie import Specie

class MatlabSpectrumsLibrary(SpectrumsLibrary):
	"""
	@inherit documentation
	"""
	def __init__(self, speciesLibrary, spectrumsDirectory):
		try:
			os.makedirs(spectrumsDirectory)
		except OSError:
			pass
		self.speciesLibrary = speciesLibrary
		self.prensentSpeciesByKey = {}
		self.spectrumsDirectory = spectrumsDirectory
		self.taggedSpectrums = []
		self.untaggedSpectrums = []
		for fileName in glob.glob(self.spectrumsDirectory + '/*.mat'):
			matlabData = sio.loadmat(fileName)
			try:
				key = ''.join(matlabData['specieKey'])
				try:
					deviceConfig = ''.join(matlabData['deviceConfig'])
				except:
					deviceConfig = None
				self.taggedSpectrums.append(TaggedSpectrum(
					matlabData['points'],
					self.speciesLibrary.getSpeciesByKey()[key],
					int(matlabData['indice']),
					fileName=fileName,
					deviceConfig=deviceConfig
				))
				if(key not in self.prensentSpeciesByKey.keys()):
					self.prensentSpeciesByKey[key] = self.speciesLibrary.getSpeciesByKey()[key]
			except KeyError:
				self.untaggedSpectrums.append(Spectrum(matlabData['points'], fileName=fileName))

	def getTaggedSpectrums(self):
		"""
		@inherit documentation
		"""
		return self.taggedSpectrums
		
	def getUntaggedSpectrums(self):
		"""
		@inherit documentation
		"""
		return self.untaggedSpectrums
		
	def getPresentSpeciesByKey(self):
		"""
		@inherit documentation
		"""
		return self.prensentSpeciesByKey

	def save(self, taggedSpectrum):
		"""
		@inherit documentation
		"""
		if taggedSpectrum.tag.key not in self.speciesLibrary.getSpeciesByKey():
			self.speciesLibrary.addSpecie(taggedSpectrum.tag)
		sio.savemat(
			self.spectrumsDirectory + '/' + taggedSpectrum.tag.key + '_' + str(taggedSpectrum.indice) + '.mat',
			{'specieKey': taggedSpectrum.tag.key, 'indice': taggedSpectrum.indice, 'points': taggedSpectrum.points, 'deviceConfig': taggedSpectrum.deviceConfig}
		)
		found = False
		indice = 0
		for existingIndice, existingTaggedSpectrum in enumerate(self.taggedSpectrums):
			if (
				existingTaggedSpectrum.tag.key == taggedSpectrum.tag.key
				and existingTaggedSpectrum.indice == taggedSpectrum.indice
			):
				found = True
				indice = existingIndice
				break
		if found:
			self.taggedSpectrums[indice] = taggedSpectrum
		else:
			self.taggedSpectrums.append(taggedSpectrum)


	def getAvailableIndiceForSpecie(self, specieKey):
		"""
		@inherit documentation
		"""
		largestIndice = 0
		for taggedSpectrum in self.taggedSpectrums:
			if taggedSpectrum.tag.key == specieKey and taggedSpectrum.indice > largestIndice:
				largestIndice = taggedSpectrum.indice
		return largestIndice + 1
