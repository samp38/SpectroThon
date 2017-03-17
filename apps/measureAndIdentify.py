import sys
import os
sys.path.insert(0, os.path.abspath('..'))
import romeo
import argparse
from termcolor import colored

# Parse arguments
parser = argparse.ArgumentParser(description='Identify spectrums in the candidates folder. Species and learning spectrums directory are required.')
parser.add_argument('-s', '--speciesDir', required=True,
                    help='path to the species folder')
parser.add_argument('-l', '--learningSpectrumsDir', required=True,
                    help='path to the learning spectrums folder')
args = vars(parser.parse_args())


# Open databases
print("Opening species database located at " + str(os.path.abspath(args['speciesDir'])))
speciesLib = romeo.MatlabSpeciesLibrary(args['speciesDir'])
speciesByKey = speciesLib.getSpeciesByKey()
print("Opening spectrum database located at " + str(os.path.abspath(args['learningSpectrumsDir'])))
taggedSpectrumsDatabase = romeo.MatlabSpectrumsLibrary(speciesLib, args['learningSpectrumsDir'])
print("Computing PCA")
pca = romeo.Pca(taggedSpectrumsDatabase.getTaggedSpectrums(), range(888,1335,3))
print("OK")
device = romeo.RomeoSpectrometer(avgScansNumber=1, xSmooth=2)
device.initialize(True)
keyPressed = ''
while(keyPressed != 'q'):
	raw_input('Please place your sample in the cuvette for measurement and press [ENTER]\n>>>')
	spectrum = device.getSpectrum(True)
	spectrum.plot()
	resPCA = pca.identify(spectrum)
	if resPCA:
		for res in resPCA:
			print('{0:30}'.format(res[0].key) + "{0:.3f}".format(res[1]) + "%")
		print("\n")
	else:
		print("No match found")
	keyPressed = raw_input('Press [ENTER] to measure agaun or [q] to quit\n>>>')
