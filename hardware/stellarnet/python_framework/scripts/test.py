#!/usr/bin/env python

import sys
sys.path.append('/Users/sam/Documents/IDV/projects/Spectro/hardware/stellarnet/files_to_copy')
import stellarnet as st
import numpy as np
import matplotlib.pyplot as plt
import Tkinter, tkFileDialog
import datetime
import os
import scipy.io as sio

spectro_id = 0
integration_time = 2
scans_avg_number = 1
lambdas = np.empty([512,1])
xsmooth = 0

def saveSpectrum(spectrum):
	root = Tkinter.Tk()
	dirname = tkFileDialog.askdirectory(parent=root, initialdir="/Users/sam/Documents/IDV/projects/Spectro/hardware/stellarnet/scripts/savedSpectrums", title='Please select a directory')
	if len(dirname ) <= 0:
		print("Bad file name")
		return False
	else:
		name = dirname.split('/')[-1]
		f = open(dirname+'/'+name+'.txt', 'w')
		f.write("Date : " + str(datetime.date.today()) + '\n')
		f.write(str(stellarnetDevice.get_config()))
		output = {}
		output['lambda'] = lambdas
		output['spectrum'] = spectrum
		sio.savemat(dirname+'/'+name, output, oned_as='column')
	
def initSpectro():
	devices = st.find_devices()
	if(len(devices) == 0):
		raise RuntimeError("no spectrometer detected :-(")
	device = devices[0]
	device.print_info()
	print(spectro_id)
	device.set_config(int_time=integration_time, scans_to_avg=scans_avg_number, x_smooth=xsmooth)
	config = device.get_config()
	print(config)
	for px in range(0,len(lambdas)):
		lambdas[px] = device.compute_lambda(px)
	return device

stellarnetDevice = initSpectro()
saveSpectrum(stellarnetDevice.read_spectrum())

#spectrum = device.read_spectrum()
#plt.plot(lambdas, spectrum)
#plt.show()
