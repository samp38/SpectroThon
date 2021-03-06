import numpy
import scipy.linalg as la
from scipy.spatial import distance
import scipy.linalg as la
import matplotlib.pyplot as plt
import math


class Pca(object):
	"""
	Pca (Principal components analysis) builds a model and matches measured spectrums
	"""
	def __init__(self, taggedSpectrums, wavelengthRange, xSmooth=0):
		"""
		taggedSpectrums is a list of tagged spectrum objects
		XSmooth parameter is used to apply box car averaging on the learning spectrums (0, 1, 2, 3 or 4)
		"""
		self.taggedSpectrums = taggedSpectrums
		self.wavelengthRange = wavelengthRange
		# Build the learning values array
		learningValues = numpy.array([[spectrum.getAbsorbance(wavelength, xSmooth) for wavelength in wavelengthRange] for spectrum in taggedSpectrums])
		
		# Center learning values by its mean
		learningValues_centered = numpy.matrix([[value - numpy.mean(line) for value in line] for line in learningValues])
		
		# Calculate model
		C = numpy.dot(numpy.transpose(learningValues_centered),learningValues_centered)/(learningValues_centered.shape[0]-1)
		eigen = la.eig(C)
		self.loading = eigen[1]
		D = eigen[0]
		scores = numpy.dot(learningValues_centered, self.loading)
		self.scoresMap = numpy.matrix([(numpy.real(score.item((0, 0))), numpy.real(score.item((0, 1)))) for score in scores])
		
		self.largestIndiceByTagKey = {}
		tagsByTagKey = {}
		scoresCloudByTagKey = {}
		for counter, scores in enumerate(self.scoresMap):
			if(self.taggedSpectrums[counter].tag.key in scoresCloudByTagKey):
				scoresCloudByTagKey[self.taggedSpectrums[counter].tag.key].append(scores)
			else:
				scoresCloudByTagKey[self.taggedSpectrums[counter].tag.key] = [scores]
			tagsByTagKey[self.taggedSpectrums[counter].tag.key] = self.taggedSpectrums[counter].tag
			if (self.taggedSpectrums[counter].tag.key not in self.largestIndiceByTagKey or self.taggedSpectrums[counter].indice > self.largestIndiceByTagKey[self.taggedSpectrums[counter].tag.key]):
				self.largestIndiceByTagKey[self.taggedSpectrums[counter].tag.key] = self.taggedSpectrums[counter].indice
		self.bivariateGaussiansAndTags = []
		for tagKey, scoresCloud in scoresCloudByTagKey.iteritems():
			scoresCloudAsMatrix = numpy.transpose(numpy.matrix(numpy.array(scoresCloud)))
# 			self.bivariateGaussiansAndTags.append((
# 				numpy.random.multivariate_normal(numpy.squeeze(numpy.asarray(numpy.mean(scoresCloudAsMatrix, axis=1))), numpy.cov(scoresCloudAsMatrix)),
# 				tagsByTagKey[tagKey]
# 			))
			self.bivariateGaussiansAndTags.append((
				numpy.squeeze(numpy.asarray(numpy.mean(scoresCloudAsMatrix, axis=1))),
				numpy.cov(scoresCloudAsMatrix),
				tagsByTagKey[tagKey],
				numpy.random.multivariate_normal(numpy.squeeze(numpy.asarray(numpy.mean(scoresCloudAsMatrix, axis=1))), numpy.cov(scoresCloudAsMatrix), 200),
				scoresCloudAsMatrix
			))

	def plotPCA(self):
		for toto in self.bivariateGaussiansAndTags:
			caca = numpy.transpose(toto[3])
			label = str(toto[2].key)
			x = caca[0]
			y = caca[1]
			plt.scatter(x, y, c=numpy.random.rand(3,1))
			plt.text(numpy.mean(x), numpy.mean(y), label)
			plt.axis('equal')
		plt.grid(True)
		plt.show()

	def identify(self, spectrum, xSmooth=0):
		"""
		Tries to match spectrum with the model and returns the closest candidate
		xSmooth parameter is used to apply box car averaging on the candidate spectrum (0, 1, 2, 3 or 4)
		"""
		candidateValues = numpy.array([spectrum.getAbsorbance(wavelength, xSmooth) for wavelength in self.wavelengthRange])
		# Center learning values by its mean
		candidateValues_centered = numpy.array([value - numpy.mean(candidateValues) for value in candidateValues])
		ns = numpy.dot(candidateValues_centered,self.loading)
		ns = numpy.real(ns)		
		candidatePCA = (ns[0],ns[1])
		resultPCA = []
		normSum = 0
		for toto in self.bivariateGaussiansAndTags:
			# print toto[2].key
			covMatrix = toto[1]
			covMatrixInv = la.inv(toto[1])
			# print covMatrixInv
			det = la.det(covMatrix)
			if(numpy.isclose(det, 0)):
				det = numpy.finfo(float).eps
			x_mu = candidatePCA - toto[0]
			norm_const = 1.0/math.pow(math.pow(2*math.pi,2) * det, 0.5)
			# titi = numpy.dot(x_mu, covMatrixInv)
			pdf = norm_const * math.exp(-0.5 * numpy.dot(  numpy.dot(x_mu, covMatrixInv),   numpy.transpose(x_mu)  ))
			normSum += pdf
			resultPCA.append([toto[2], pdf])
			resultPCA = sorted(resultPCA, key=lambda subRes: subRes[1], reverse=True)
		# Normalize pdf
		for res in resultPCA:
			if(normSum > 0):
				res[1] = 100 * float(res[1]) / float(normSum)
			else:
				return False
			
		# Print sorted result
		# for res in resultPCA:
		# 	print(res[0]. key + "\t" + str("{0:.3f}".format(res[1])) + "%")
		return resultPCA
		
			
		# print(spectrum.name + '@' + spectrum.concentration + ' identified as : ' + str(self.taggedSpectrums[distance.cdist([(ns[0],ns[1])], self.scoresMap).argmin()].name) + '@' + str(self.taggedSpectrums[distance.cdist([(ns[0],ns[1])], self.scoresMap).argmin()].concentration))

	# def identify(self, spectrum):
	# 	"""
	# 	Tries to match spectrum with the model and returns the closest candidate
	# 	"""
	# 	candidateValues = numpy.array([spectrum.getAbsorbance(wavelength) for wavelength in self.wavelengthRange])
	# 	# Center learning values by its mean
	# 	candidateValues_centered = numpy.array([value - numpy.mean(candidateValues) for value in candidateValues])
	# 	ns = numpy.dot(candidateValues_centered,self.loading)
	# 	ns = numpy.real(ns)
	# 	print(spectrum.name + '@' + spectrum.concentration + ' identified as : ' + str(self.taggedSpectrums[distance.cdist([(ns[0],ns[1])], self.scoresMap).argmin()].name) + '@' + str(self.taggedSpectrums[distance.cdist([(ns[0],ns[1])], self.scoresMap).argmin()].concentration))
	#
	# 	# nClosestNeighbours = [self.taggedSpectrums[index] for index in distance.cdist([(ns[0],ns[1])], self.scoresMap).argsort()[:5]]
	# 	sortedIndexes = distance.cdist([(ns[0],ns[1])], self.scoresMap).argsort()[0][:10]
	# 	print('The closests neighbours are : ')
	# 	for index in sortedIndexes:
	# 		print(str(self.taggedSpectrums[index].name) + '@' + str(self.taggedSpectrums[index].concentration) + '_#' + str(self.taggedSpectrums[index].indice) + 'distance = ' + str(distance.cdist([(ns[0],ns[1])], self.scoresMap)[0][index]))
	#
	# 	# Plot learningValus map
	# 	for counter, x in enumerate(self.scoresMap):
	# 		plt.scatter(x.item(0), x.item(1), c=numpy.random.rand(3,1), label = self.taggedSpectrums[counter].name, s=200)
	# 		plt.text(x.item(0), x.item(1),str(self.taggedSpectrums[counter].name) + '@' + str(self.taggedSpectrums[counter].concentration) + '_#' + str(self.taggedSpectrums[counter].indice))
	#
	# 	## PLOT RESULT
	# 	plt.scatter(ns[0],ns[1],c=numpy.random.rand(3,1), label = "candidate", marker="H", s=400)
	# 	plt.grid(True)
	# 	plt.show()
		
		# must return a TaggedSpectrum with the same points as the given spectrum, but with a tag and indice
		
		"""
		self.largestIndiceByTagKey[idetifiedTag] += 1
		return TaggedSpectrum with indice self.largestIndiceByTagKey[identifiedTag]
		"""
		