import sys
import os
sys.path.insert(0, os.path.abspath('..'))
import romeo
import argparse
from termcolor import colored, cprint


xSmooth_learningSpectrums = 0
xSmooth_candidates        = 0

# Parse arguments
parser = argparse.ArgumentParser(description='Identify spectrums in the candidates folder. Species and learning spectrums directory are required.')
parser.add_argument('-c', '--candidatesDir', required=True,
                    help='path to the candidates folder')
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
print("Opening candidates database located at " + str(os.path.abspath(args['candidatesDir'])))
candidateSpectrumsDatabase = romeo.MatlabSpectrumsLibrary(speciesLib, args['candidatesDir'])

#
# for candidate in candidateSpectrumsDatabase.getTaggedSpectrums():
# 	for xSmooth in range(0, 5):
# 		candidate.plot(xSmooth)

pca = romeo.Pca(taggedSpectrumsDatabase.getTaggedSpectrums(), range(888,1335,3), xSmooth=xSmooth_learningSpectrums)
pca.plotPCA()
for candidate in candidateSpectrumsDatabase.getTaggedSpectrums():
	print(colored("Identifying " + candidate.tag.key, 'cyan') + " (located at " +  str(os.path.abspath(args['candidatesDir'])) + "/" + candidate.fileName + ")")
	resPCA = pca.identify(candidate, xSmooth=xSmooth_candidates)
	if(resPCA):
		for res in resPCA:
			print('{0:30}'.format(res[0].key) + "{0:.3f}".format(res[1]) + "%")
		if(resPCA[0][0].key == candidate.tag.key):
			print(colored('Success', 'green') + " identifying " + candidate.tag.key + " with " + "{0:.3f}".format(resPCA[0][1]-resPCA[1][1]) + " certainity")
		else:
			print(colored('Fail', 'red') + " identifying " + candidate.tag.key)
		print("\n")
	else:
		print("PCA FAILED")