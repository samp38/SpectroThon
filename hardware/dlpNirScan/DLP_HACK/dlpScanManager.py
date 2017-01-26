import dlpHack
import math


spectrumPointsNumber  	= 160
startLambda	  		    = 1350
endLambda	 	  		= 2000
numberOfScansToAverage 	= 10
exposureTime			= 4000

_input_                 = "-1"
renewScan               = False

lambdaValues    = []
resolution		= round(float(endLambda - startLambda)/spectrumPointsNumber, 1)
measurementTime = round(1.4 * (math.ceil(spectrumPointsNumber/24.0) + spectrumPointsNumber) * numberOfScansToAverage, 1)
pga						= -1

output = []

# Set reference
# pga = dlpHack.setReference(spectrumPointsNumber, exposureTime, numberOfScansToAverage)


pga = dlpHack.getPGA()
print pga

while(_input_ != "q"):
	_input_ = raw_input("\n[s] Scan\n[r] Set Reference\n[p] Generate Patterns\n[q] quit\n")
	if(_input_ == "s"):
		print("Performing Scan " + str(renewScan))
		dlpHack.applySettings(startLambda, endLambda, dlpHack.lambdaToPixel(startLambda), dlpHack.lambdaToPixel(endLambda), spectrumPointsNumber, resolution, exposureTime, measurementTime, numberOfScansToAverage)
		output = dlpHack.runScan(startLambda, endLambda, spectrumPointsNumber, exposureTime, numberOfScansToAverage, pga, renewScan)
		if(renewScan == False):
			renewScan = True
		if(raw_input('Save Scan? [y]/[n]') == 'y'):
			dlpHack.saveSpectrum(output)
	elif(_input_ == "r"):
		pga = dlpHack.setReference(spectrumPointsNumber, exposureTime, numberOfScansToAverage)
		renewScan = False
	elif(_input_ == "q"):
		exit(0)
	elif(_input_ == "p"):
		dlpHack.applySettings(startLambda, endLambda, dlpHack.lambdaToPixel(startLambda), dlpHack.lambdaToPixel(endLambda), spectrumPointsNumber, resolution, exposureTime, measurementTime, numberOfScansToAverage)
		dlpHack.generatePatterns(dlpHack.lambdaToPixel(startLambda), dlpHack.lambdaToPixel(endLambda), spectrumPointsNumber)
		renewScan = False
	else:
		print("Bad command")
