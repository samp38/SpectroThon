import sys
import os
sys.path.insert(0, os.path.abspath('..'))
import romeo
import argparse
import scipy.io as sio
import numpy

lambdaMin           = 900
lambdaMax           = 1400
lamdaStep           = 3


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


pairsIndexes = {}
cnt = 0
for smoothWindowSize in reversed(range(0,5)):
    print("Processing xSmooth " + str(smoothWindowSize))
    pca = romeo.Pca(taggedSpectrumsDatabase.getTaggedSpectrums(), range(lambdaMin,lambdaMax,lamdaStep), xSmooth=smoothWindowSize)
    pcaDistances = pca.getDistributionPairsDistance()
    # if first loop, keep the pairs order in a dictionary
    if cnt == 0:
        i = 0
        for pcaDistance in pcaDistances:
            print pcaDistance
            pairsIndexes[pcaDistance[0]] = i
            i += 1
        cnt += 1
	# if not first loop, keep the pair order of the first one thanks to pairsIndex dictionary
    else:
		pcaDistancesSorted = [None] * len(pcaDistances)
		
		for result in pcaDistances:
			pcaDistancesSorted[pairsIndexes.get(result[0])] = (result[0], result[1])
			# print(str(pairsIndexes.get(result[0])) + "\t" + str((result[1])))
		pcaDistances = pcaDistancesSorted
		
    sio.savemat(
        'pcaDistances_xSmooth' + '_' + str(smoothWindowSize) + '.mat',
        {'pair': [row[0] for row in pcaDistances], 'Db': [row[1] for row in pcaDistances]}
    )
# for pairsIndex in pairsIndexes:
# 	print(pairsIndex + "  " + str(pairsIndexes[pairsIndex]))