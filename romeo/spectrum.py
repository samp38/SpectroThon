import bisect
import matplotlib.pyplot as plt
import math

class Spectrum(object):
	"""Spectrum represents a measured spectrum from a Stellarnet device"""
	def __init__(self, points, fileName=None, deviceConfig=None):
		"""
		Points is a list of tuples (pixel lambda, pixel blank ADC value, pixel transmitted ADC value, pixel dark ADC value)
		"""
		self.points = tuple(points)
		self.fileName = fileName
		self.deviceConfig = deviceConfig
		self.cache = {}
				
	def _getPoint(self, xSmooth, index):
		""" Absorbance is defined as follows:
				 A(n)=-log((sample(n)-dark(n))/(ref(n)-dark(n)))
		"""
		
		if(not xSmooth in self.cache):
			smoothed_blank    = Spectrum._smooth_data([point[1] for point in self.points], xSmooth)
			smoothed_measures = Spectrum._smooth_data([point[2] for point in self.points], xSmooth)
			smoothed_dark     = Spectrum._smooth_data([point[3] for point in self.points], xSmooth)
			self.cache[xSmooth]=[]
			for i in range(0,len(self.points)):
				num = smoothed_measures[i] - smoothed_dark[i]
				denom = smoothed_blank[i] - smoothed_dark[i]
				signalRatio = num/denom
				if(denom < 0):
					print("WARNING : dark is brighter than blank @ " + str(self.points[i][0]))
				if(num < 0):
					print("WARNING : dark is brighter than transmitted signal @ " + str(self.points[i][0]))
				if(signalRatio <= 0):
					# signalRatio = 1e-1
					print("WARNING : Negative absorbance @ " + str(self.points[i][0]))
					signalRatio = 1
				self.cache[xSmooth].append(tuple([self.points[i][0], smoothed_blank[i], smoothed_measures[i], smoothed_dark[i], -math.log(signalRatio, 10)]))
				# self.cache[xSmooth].append(tuple([self.points[i][0], smoothed_blank[i], smoothed_measures[i], smoothed_dark[i], signalRatio]))
			self.cache[xSmooth] = tuple(self.cache[xSmooth])
		return self.cache[xSmooth][index]
					
		
	
	def getAbsorbance(self, wavelength, xSmooth=0):
		if(wavelength < self._getPoint(xSmooth, 0)[0]):
			return self._getPoint(xSmooth, 0)[4]
		elif(wavelength >= self._getPoint(xSmooth, -1)[0]):
			return self._getPoint(xSmooth, -1)[4]
		else:
			indexSup = bisect.bisect([point[0] for point in self.points], wavelength)
			indexInf = indexSup - 1
			slope = float(self._getPoint(xSmooth, indexSup)[4] - (self._getPoint(xSmooth, indexInf)[4])) / float(self._getPoint(xSmooth, indexSup)[0] - self._getPoint(xSmooth, indexInf)[0])
			intercept = (self._getPoint(xSmooth, indexInf)[4]) - (self._getPoint(xSmooth, indexInf)[0]) * slope
			return slope * wavelength + intercept
			
	
	def plot(self, xSmooth=0):
		# Two subplots, the axes array is 1-d
		f, axarr = plt.subplots(2, sharex=True)
		axarr[0].plot(
			[point[0] for point in self.points], 
			[self._getPoint(xSmooth, index)[1] for index in range(0, len(self.points))]
		)
		axarr[0].set_title('Blank')
		axarr[1].plot([point[0] for point in self.points],  [self._getPoint(xSmooth, index)[4] for index in range(0, len(self.points))])
		axarr[1].set_title('Absoption')
		axarr[1].set_xlabel('[nm]')
		plt.grid(True)
		plt.show()
	
	
	@staticmethod
	def _smooth_data(src, xSmooth):
		"""Apply boxcar smoothing to data."""
		_WINDOW_MAP = {0:0, 1:5, 2:9, 3:17, 4:33}
		win_span = _WINDOW_MAP[xSmooth]
		if win_span == 0:
			return src
		
		# Smooth middle, start indexes are inclusive, limit indexes are exclusive
		pixels = len(src)
		dst = [0]*pixels
		half_span = win_span/2
		src_start = half_span
		src_limit = pixels - half_span
		win_start = 0
		win_limit = win_span
		win_sum = sum(src[win_start:win_limit])
		dst[src_start] = win_sum/win_span
		for i in xrange(src_start + 1, src_limit):
			win_sum += src[win_limit] - src[win_start]
			dst[i] = win_sum/win_span
			win_start += 1
			win_limit += 1
		    		
		# Smooth left end
		src_start = 0
		win_sum = src[src_start]
		dst[src_start] = src[src_start]
		j = src_start + 1
		for i in xrange(j, half_span):
			win_sum += src[j + 0] + src[j + 1]
			j += 2
			dst[i] = win_sum/j
			
		# Smooth right end
		src_start = pixels - 1
		win_sum = src[src_start]
		dst[src_start] = src[src_start]
		j = src_start - 1
		for i in xrange(j, pixels - half_span - 1, -1):
			win_sum += src[j - 0] + src[j - 1]
			j -= 2
			dst[i] = win_sum/(src_start - j)
			
		return dst
	