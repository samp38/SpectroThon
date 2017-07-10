import sys
import os
sys.path.insert(0, os.path.abspath('..'))
import romeo
import argparse

lambdaMin 				  = 900
lambdaMax 				  = 1400
lamdaStep				  = 3


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



with open('optimizeOutput', 'w') as f:
	# write parameters to output file
	f.write("lambda min [nm] ; lambda max [nm] ; step [nm] ; xsmooth ; score\n")
	for smoothWindowSize in range(0,5):
		print("Window size = " + str(smoothWindowSize))
		pca = romeo.Pca(taggedSpectrumsDatabase.getTaggedSpectrums(), range(lambdaMin,lambdaMax,lamdaStep), xSmooth=smoothWindowSize)
		score = pca.evaluatePCA()
		f.write(str(lambdaMin) + " ; " + str(lambdaMax) + " ; " + str(lamdaStep) + " ; " + str(smoothWindowSize) + " ; " + str(score) + "\n")

