import sys
import os
sys.path.insert(0, os.path.abspath('..'))
import romeo
import argparse
from termcolor import colored, cprint


xSmooth_learningSpectrums = 2

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


pca = romeo.Pca(taggedSpectrumsDatabase.getTaggedSpectrums(), range(888,1300,3), xSmooth=xSmooth_learningSpectrums)
pca.plotPCA()