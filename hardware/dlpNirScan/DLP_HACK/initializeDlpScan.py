import pexpect
import math
import string
import random

spectrumPointsNumber  	= 85
startLambda	  		    = 1350
endLambda	 	  		= 2450
numberOfScansToAverage 	= 8
exposureTime			= 10000

resolution		= round(float(endLambda - startLambda)/spectrumPointsNumber, 1)
measurementTime = round(1.4 * (math.ceil(spectrumPointsNumber/24.0) + spectrumPointsNumber) * numberOfScansToAverage, 1)

# lambdaToPixel converts a wavelength to the units used by the DLP NIRscan.
def lambdaToPixel(wavelength):
	return int(round(-1695.135009765625 + 1.11876213550567626953125 * wavelength + 0.000106355393654666841030120849609375 * wavelength * wavelength))

# run executes the given bash lines on the remote server.
# lines must be an array of strings
# prefer double-quotes (") over simple-quotes (') to avoid escaping issues
def run(lines):
    child = pexpect.spawn('ssh root@192.168.0.10 \'' + ';'.join(lines) + '\'')
    child.expect('.*assword:.*')
    child.sendline('')
    child.expect(pexpect.EOF, timeout = None)
    return child.before[2:-1]

# generate pattern
print run([
	"cd /usr/share/matrix-gui-2.0",
	"rm patterns/*.csv",
	"rm patterns/*.bmp",	
	"rm patterns/*.sdf",		
	"rm tmp/*",		
	"rm *.bmp",		
	"dlp_nirscan -A" + str(lambdaToPixel(startLambda)) + " -Z" + str(lambdaToPixel(endLambda)) + " -N" + str(spectrumPointsNumber),
	"cd patterns/",
	"dlp_nirscan -Pscan.sdf",
	"count=0",
    "for entry in *",
	"    do if [[ $entry == *.bmp ]]",
	"        then convert $entry -virtual-pixel Black -filter point -interpolate nearestneighbor -distort polynomial \"2 $(cat /usr/share/matrix-gui-2.0/calibration_data/control_points.txt)\" scan_img.bmp",
	"        mv scan_img.bmp $entry",
	"        count=$((count+1))",
	"    fi",
	"done",
	"dlp_nirscan -l$count",	
	"cd .. ",
])

# save the used settings
print run([
	"cd /usr/share/matrix-gui-2.0",
	"echo \"" + "\n".join([
		str(startLambda),
		str(endLambda),
		str(resolution),
		str(measurementTime),
		str(numberOfScansToAverage),
		str(spectrumPointsNumber),
		str(lambdaToPixel(startLambda)),
		str(lambdaToPixel(endLambda)),
	]) + "\n\" > defaultParameters.txt",
])

# run the reference scan
print run([
	"cd /usr/share/matrix-gui-2.0",
	"cd patterns/",
	"count=0",
    "for entry in *",
	"    do if [[ $entry == *.bmp ]]",
	"        then count=$((count+1))",
	"    fi",
	"done",
	"dlp_nirscan -l$count",
	"cd ..",
	"cd custom_scan_data/reference_scan_data/",
	"dlp_nirscan -S" + str(spectrumPointsNumber) + " -E1400 -fref_readings.txt -L2",
	"mv avg_readings.txt ref_readings_avg.txt",
	"cd ..",
	"cd ..",
	"rm tmp/*",
])
