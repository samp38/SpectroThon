import pexpect
import math
import string
import random
import matplotlib.pyplot as plt

spectrumPointsNumber  	= 85
startLambda	  		    = 1350
endLambda	 	  		= 2450
numberOfScansToAverage 	= 4
exposureTime			= 1400
pga						= 32

resolution		= round(float(endLambda - startLambda)/spectrumPointsNumber, 1)
measurementTime = round(1.4 * (math.ceil(spectrumPointsNumber/24.0) + spectrumPointsNumber) * numberOfScansToAverage, 1)

# lambdaToPixel converts a wavelength to the units used by the DLP NIRscan.
def lambdaToPixel(wavelength):
	return int(round(-1695.135009765625 + 1.11876213550567626953125 * wavelength + 0.000106355393654666841030120849609375 * wavelength * wavelength))

def pixelToLambda(pixel):
	return int(round(1344.4271240234375 + 0.706179559230804443359375 * pixel -0.0000297453443636186420917510986328125 * (pixel ** 2)))
	
# getRandomName generates a random name with the .txt extension.
def getRandomName():
	return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8)) + ".txt"

# run executes the given bash lines on the remote server.
# lines must be an array of strings
# prefer double-quotes (") over simple-quotes (') to avoid escaping issues
def run(lines):
    child = pexpect.spawn('ssh root@192.168.0.10 \'' + ';'.join(lines) + '\'')
    child.expect('.*assword:.*')
    child.sendline('')
    child.expect(pexpect.EOF, timeout = None)
    return child.before[2:-1]

lambdaValues = []

columnsPerPattern = math.floor((lambdaToPixel(endLambda)-lambdaToPixel(startLambda)+1)/spectrumPointsNumber)
extraColumns = (lambdaToPixel(endLambda)-lambdaToPixel(startLambda)+1)%spectrumPointsNumber
extraColumnsFrequency = math.floor(spectrumPointsNumber/extraColumns) if extraColumns > 0 else 0
currentPatternFirstPixel = lambdaToPixel(startLambda)
for currentPattern in range(0, spectrumPointsNumber):
    nextPatternFirstPixel = currentPatternFirstPixel + columnsPerPattern
    if extraColumns > 0:
        if currentPattern % extraColumnsFrequency == 0:
            nextPatternFirstPixel += 1
            extraColumns -= 1
    lambdaValues.append(pixelToLambda((currentPatternFirstPixel + nextPatternFirstPixel - 1) / 2))
    currentPatternFirstPixel = nextPatternFirstPixel

# Run sample scan for the first time
print run([
	"cd /usr/share/matrix-gui-2.0",
	"cd patterns/",
	"count=0",
    "for entry in *",
	"    do case $entry in *.bmp) count=$((count+1));",
	"    esac",
	"done",
	"dlp_nirscan -l$count",
	"cd ..",
	"for i in {1..20}",
	"    do dlp_nirscan -g" + str(pga),
	"    if [ $? -eq 0 ]",
	"        then break",
	"    fi",
	"done",
	"if [ $i -eq 20 ]",
	"    then echo \"pga_setting_failed\"",
	"    exit 0",
	"fi",
	"cd custom_scan_data/sample_scan_data/",
	"dlp_nirscan -S" + str(spectrumPointsNumber) + " -E" + str(exposureTime) + " -fpython_custom_scan.txt" + " -L" + str(numberOfScansToAverage),
	"mv avg_readings.txt python_custom_scan_avg.txt",
	"dlp_nirscan -G -r../reference_scan_data/ref_readings_avg.txt -fpython_custom_scan_avg.txt",
	"if [ $? -eq 255 ]",
	"    then echo \"failed\"",
	"    exit 0",
	"fi",
	"cd ..",
	"cd ..",
	"rm tmp/*",
]);

referenceData    = [int(value, 16) for value in run(["cat /usr/share/matrix-gui-2.0/custom_scan_data/reference_scan_data/ref_readings_avg.txt"]).split('\n')]
referenceDataRaw = [int(value, 16) for value in run(["cat /usr/share/matrix-gui-2.0/custom_scan_data/reference_scan_data/ref_readings_00_raw.txt"]).split('\n')]
sampleValues     = [int(value, 16) for value in run(["cat /usr/share/matrix-gui-2.0/custom_scan_data/sample_scan_data/python_custom_scan_avg.txt"]).split('\n')]
sampleValuesRaw  = [int(value, 16) for value in run(["cat /usr/share/matrix-gui-2.0/custom_scan_data/sample_scan_data/python_custom_scan_00_raw.txt"]).split('\n')]
absorbanceValues = [float(value) for value in run(["cat /usr/share/matrix-gui-2.0/custom_scan_data/sample_scan_data/python_custom_scan_avg_absp.txt"]).split('\n')]
print("length of lambdas : " + str(len(lambdaValues)))
print("length of absobance values : " + str(len(absorbanceValues)))
plt.plot(lambdaValues, absorbanceValues)
plt.show()
