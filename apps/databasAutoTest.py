import sys
import os
sys.path.insert(0, os.path.abspath('..'))
import romeo
import argparse
import itertools


# PCA parameters
xSmooth_learningSpectrums = 2
xSmooth_candidates = 2


# Parse arguments
parser = argparse.ArgumentParser(description='Runs database auto test. Exclude some spectrums from database and try to identify them. Species and spectrums database directory are required.')
parser.add_argument('-s', '--speciesDir', required=True,
                    help='path to the species folder')
parser.add_argument('-d', '--databaseDir', required=True,
                    help='path to the database folder')
args = vars(parser.parse_args())


# Open databases
print("Opening species database located at " + str(os.path.abspath(args['speciesDir'])))
speciesLib = romeo.MatlabSpeciesLibrary(args['speciesDir'])
print("Opening spectrum database located at " + str(os.path.abspath(args['databaseDir'])))
taggedSpectrumsDatabase = romeo.MatlabSpectrumsLibrary(speciesLib, args['databaseDir'])

rawSpectrumsList = taggedSpectrumsDatabase.getTaggedSpectrums()
presentSpecies   = taggedSpectrumsDatabase.getPresentSpeciesByKey()

for specieKey in presentSpecies.keys():
	# Get index of all spactrums whose specie key matches specieKey
	originalIndex = [(index, s) for index, s in enumerate(rawSpectrumsList) if(s.tag.key == specieKey)]
	print('________________________________________________________________________________________________________________________________________________')
	print('Parsing ' + specieKey)
	print(originalIndex)
	# Iterate over subsets of the current specie
	cnt = 0
	for subset in itertools.combinations(originalIndex, 2):
		if( cnt < 1):
			cnt += 1
			subsetIndexes = [r[0] for r in subset]
			# Build the learning spectrums and candidates databases
			learning = []
			for index, spectrum in enumerate(rawSpectrumsList):
				if(index not in subsetIndexes):
					learning.append(spectrum)
			candidates = [r[1] for r in subset]
			
			
			# Compute PCA for the current configuration
			pca = romeo.Pca(learning, range(900,1400,3), xSmooth=xSmooth_learningSpectrums)
			
			# launch recognition test for the current candidates group
			res = pca.identifyGroup(candidates, xSmooth=xSmooth_candidates)