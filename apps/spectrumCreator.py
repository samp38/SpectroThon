import sys
import os
sys.path.insert(0, os.path.abspath('..'))
import romeo
import argparse
from time import sleep

parser = argparse.ArgumentParser(description='Add a spectrum to a spectrums library.')
parser.add_argument('-s', '--speciesDir', required=True,
                    help='path to the species folder')
parser.add_argument('-f', '--spectrumsDir', required=True,
                    help='path to the folder in which you want to save your spectrum')

args = vars(parser.parse_args())

# Start Spectrometer
device = romeo.RomeoSpectrometer(integrationTime=2, avgScansNumber=4, xSmooth=0)
device.initialize(True)
key = ''
while(key != 'q'):
	speciesLib = romeo.MatlabSpeciesLibrary(args['speciesDir'])
	speciesByKey = speciesLib.getSpeciesByKey()
	createNewSpecie = False
	specie = None
	if(len(speciesByKey) != 0):
		for index, key in enumerate(sorted(speciesByKey.keys())):
			print('[' + str(index) + '] ' + str(key))
		key = (raw_input('Select a specie by index or [ENTER] to create a new one, [q] to quit\n>>> '))
		if(key == 'q'):
			break
		if(key != ''):
			index = int(index)
			specie = speciesLib.getSpeciesByKey()[sorted(speciesLib.getSpeciesByKey())[index]]
			print('you chose : ' + specie.key)
		else:
			createNewSpecie = True
	else:
		createNewSpecie = True

	if(createNewSpecie):
		name = raw_input("Enter specie's name\n>>> ")
		concentration = raw_input("Enter specie's concentration\n>>> ")
		specie = romeo.Specie(name, name+'@'+concentration , concentration)
		print('you created : ' + specie.key)
	spectrumsLibrary = romeo.MatlabSpectrumsLibrary(speciesLib, args['spectrumsDir'])
	
	raw_input('Please place your sample in the cuvette for measurement and press [ENTER]\n>>>')
	spectrum = device.getSpectrum(True)
	taggedSpectrum = romeo.TaggedSpectrum(spectrum.points, specie, spectrumsLibrary.getAvailableIndiceForSpecie(specie.key), deviceConfig=spectrum.deviceConfig)
	
	# save matlab files
	speciesLib.addSpecie(specie)
	spectrumsLibrary.save(taggedSpectrum)
