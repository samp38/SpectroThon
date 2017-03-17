import sys
import os
sys.path.insert(0, os.path.abspath('.'))
import stellarnet
from spectrum import Spectrum
from time import sleep

class RomeoSpectrometer(object):
	"""
	RomeoSpectrometer is a wrapper around Stellarnet spectrometer with utility functions to generate spectrum objects
	"""
	def __init__(self, integrationTime=2, avgScansNumber=1, xSmooth=0):
		"""
		On initialization, we connect to the first available device
		"""
		devices = stellarnet.find_devices()
		if(len(devices) == 0):
			raise RuntimeError("no spectrometer detected :-(")
		self.device = devices[0]
		self.device.set_config(int_time=integrationTime, scans_to_avg=avgScansNumber, x_smooth=xSmooth)
		tempValues = self.device.read_spectrum()
		self.lambdas = []
		for px in range(0,len(tempValues)):
			self.lambdas.append(self.device.compute_lambda(px))
		self.blank = None
		self.blankDeviceConfig = None
		self.dark = None
		self.darkDeviceConfig = None
		print(self.device.get_config())
	
	def getSpectrum(self, verbose=False):
		"""
		Read the spectrum and return Spectrum object
		"""
		activeDeviceConfig = self.device.get_config()
		if(activeDeviceConfig != self.blankDeviceConfig):
			raise RuntimeError("The confuration of the device has changed since blank measurement, cannot get relevant spectrum")
		if(activeDeviceConfig != self.darkDeviceConfig):
			raise RuntimeError("The confuration of the device has changed since dark measurement, cannot get relevant spectrum")
		if(verbose):
			print(activeDeviceConfig)
		sleep(0.3)
		if(self.blank == None):
			raise RuntimeError("generateBlankSpectrum must be called before getSpectrum")
		if(self.dark == None):
			raise RuntimeError("generateDarkSpectrum must be called before getSpectrum")
		spectrum = None
		success = False
		while(not success):
			try:
				spectrum = self.device.read_spectrum()
				success = True
			except stellarnet.TimeoutError:
				pass
			
		if(max(spectrum) > 65534):
			raise RuntimeError("SPECTROMETER WARNING : your measurement seems saturated, please check its shape and adjust integration time")
		points = []
		dynamic = 100.0*(float(max(spectrum))/65535.0)
		for i in range(0, len(spectrum)):
			points.append((self.lambdas[i], self.blank[i], spectrum[i], self.dark[i]))
		if(verbose):
			print('Spectrum measured, dynamic is ' + str("%.1f" % dynamic) + ' %')
		return Spectrum(points, deviceConfig=activeDeviceConfig)
		
	def generateDarkSpectrum(self, verbose=False):
		"""
		generateDarkSpectrum reads the spectrum and stores it as dark for future spectrums
		"""
		self.darkDeviceConfig = self.device.get_config()
		success = False
		while(not success):
			try:
				self.dark = self.device.read_spectrum()
				sleep(0.3)
				success = True
			except stellarnet.TimeoutError:
				pass
		dynamic = 100.0*(float(max(self.dark))/65535.0)
		if(max(self.blank) > 65534):
			raise RuntimeError("SPECTROMETER WARNING : your measurement seems saturated, please check its shape and adjust integration time")
		if(verbose):
			print('Dark set, dynamic is ' + str("%.1f" % dynamic) + ' %')
	
	def generateBlankSpectrum(self, verbose=False):
		"""
		generateBlankSpectrum reads the spectrum and stores it as blank for future spectrums
		"""
		self.blankDeviceConfig = self.device.get_config()
		success = False
		while(not success):
			try:
				self.blank = self.device.read_spectrum()
				sleep(0.3)
				success = True
			except stellarnet.TimeoutError:
				pass
		dynamic = 100.0*(float(max(self.blank))/65535.0)
		if(max(self.blank) > 65534):
			raise RuntimeError("SPECTROMETER WARNING : your measurement seems saturated, please check its shape and adjust integration time")
		if(verbose):
			print('Blank set, dynamic is ' + str("%.1f" % dynamic) + ' %')
				
		
	def autoTuneIntegrationTime_dicho(self, verbose=False):
		"""
		Turn off averaging and find the optimal exposure time for the sample in place (dichotomy), then restore averaging
		"""
		maxIntTime = 150
		minIntTime = 2
		oldConfig = self.device.get_config()
		integrationTime = -1
		while(True):
			prev_intTime = integrationTime
			integrationTime = (maxIntTime + minIntTime) // 2
			sleep(0.3)
			self.device.set_config(int_time=integrationTime, scans_to_avg=1, x_smooth=0)
			maxValue = max(self.device.read_spectrum())
			if(verbose):
				print(str(integrationTime) + 'ms  -->  maxValue = ' + str(maxValue))
			if(maxValue > 58500 and maxValue <= 64500):
				break
			elif(maxValue > 64000):
				maxIntTime = integrationTime
			else:
				minIntTime = integrationTime
			if(integrationTime == prev_intTime):
				break
		if(verbose):
			print('Optimal Integration Time : ' + str(integrationTime) + 'ms')
		# Restore old average and xsmooth settings
		self.device.set_config(int_time=integrationTime, scans_to_avg=oldConfig['scans_to_avg'], x_smooth=oldConfig['x_smooth'])

		
		
	def initialize(self, verbose=False):
		"""
		Achieves integration time autotune and sets blank spectrum
		"""
		raw_input('Please place the blank in the cuvette for exposure time autotune & blank reading and press [ENTER]\n>>>')
		self.autoTuneIntegrationTime_dicho(verbose)
		self.generateBlankSpectrum(verbose)
		raw_input('Please turn off the light source to set the sensor dark spectrum and press [ENTER]\n>>>')
		self.generateDarkSpectrum(verbose)
		
