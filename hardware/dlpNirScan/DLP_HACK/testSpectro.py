#!/usr/bin/env python

import urllib
import urllib2
import time
import math
import string
import random
import sys

spectrumPointsNb  		= 85
start_lambda	  		= 1350
end_lambda	 	  		= 2450
numberOfScanToAverage 	= 2
exposure_time			= 1400

resolution		 = round(float(end_lambda - start_lambda)/spectrumPointsNb,1)
measurement_time = round(1.4 * (math.ceil(spectrumPointsNb/24.0) + spectrumPointsNb) * numberOfScanToAverage,1)

def lambdaToPx(wavelength):
	return int(round(-1695.135009765625 + 1.11876213550567626953125 * wavelength + 0.000106355393654666841030120849609375 * wavelength * wavelength))

def getRandomName():
	return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8)) + ".txt"

# GENERATE PATTERN
randomFileName = getRandomName()

print 'Send script to server'

urllib2.urlopen('http://192.168.0.10/write_file.php', urllib.urlencode({
	'a': "\n".join([
		"exec",
		"rm /etc/default/dropbear",
		"reboot"
	]),
	'filename': 'scan.sh',
}))

"""
urllib2.urlopen('http://192.168.0.10/write_file.php', urllib.urlencode({
	'a': "\n".join([
		"exec",
		"rm patterns/*.csv",
		"rm patterns/*.bmp",	
		"rm patterns/*.sdf",		
		"rm tmp/*",		
		"rm *.bmp",		
		"dlp_nirscan -A" + str(lambdaToPx(start_lambda)) + " -Z" + str(lambdaToPx(end_lambda)) + " -N" + str(spectrumPointsNb),
		"cd patterns/",
		"dlp_nirscan -Pscan.sdf",
		"count=0",
	    "for entry in *",
		"    do",
        
		"		case $entry in *.bmp)",
		'			convert $entry -virtual-pixel Black  -filter point -interpolate nearestneighbor -distort polynomial "2 $(cat /usr/share/matrix-gui-2.0/calibration_data/control_points.txt)" scan_img.bmp',
		"			mv scan_img.bmp $entry",
		"			count=$((count+1));;",
		"		esac",
		"	done",
		"dlp_nirscan -l$count",	
		"cd .. ",
		"dlp_nirscan -S" + str(spectrumPointsNb) + " -E1400 -fcustom_scan",
	]),
	'filename': 'scan.sh',
}))
"""

print 'Send execute command'
urllib2.urlopen('http://192.168.0.10/run_scan.php')

print 'Check if the script is done'
while(True):
	
	# DEBUG	
	try:
		logContent = urllib2.urlopen('http://192.168.0.10/tmp/python_log.txt')
		print 'log content: ' + logContent.read()
	except urllib2.HTTPError:
		print 'log file not found'

	try:		
		if 'OK' in urllib2.urlopen('http://192.168.0.10/tmp/' + randomFileName).read():
			break	
	except urllib2.HTTPError:
		pass
	sys.stdout.flush()
	time.sleep(0.1)

urllib2.urlopen('http://192.168.0.10/write_file.php', urllib.urlencode({
	'a': "\n".join([
		str(start_lambda),
		str(end_lambda),
		str(resolution),
		str(measurement_time),
		str(numberOfScanToAverage),
		str(spectrumPointsNb),
		str(lambdaToPx(start_lambda)),
		str(lambdaToPx(end_lambda)),
		""
	]),
	'filename': 'defaultParameters.txt',
}))

# PERFORM REFERENCE SCAN
print "performing reference",
randomFileName = getRandomName()
urllib2.urlopen('http://192.168.0.10/write_file.php', urllib.urlencode({
	'a': "\n".join([
		"set -e",
		"exec 1> log.txt",
		"cd patterns/",
		"for entry in *",
		"do",
		"	case $entry in *.bmp)",
		"		count=$((count+1));;",
		"	esac",
		"done",
		"dlp_nirscan -l$count",
		"cd ..",
		"cd custom_scan_data/reference_scan_data/",
		"dlp_nirscan -S"+ str(spectrumPointsNb) + " -E" + str(exposure_time) + " -fref_readings.txt -L"+ str(numberOfScanToAverage),
		"mv avg_readings.txt ref_readings_avg.txt",
		"cd ..",
		"cd ..",
		"rm tmp/*",
		"echo \"OK\" > tmp/" + randomFileName,
		
	]),
	'filename': 'scan.sh',
}))

urllib2.urlopen('http://192.168.0.10/run_scan.php')

while(True):
	try:
		if 'OK' in urllib2.urlopen('http://192.168.0.10/tmp/' + randomFileName).read():
			break	
	except urllib2.HTTPError:
		pass
	time.sleep(0.1)


print('All done')

"""
urllib2.urlopen('http://192.168.0.10/run_scan.php')

urllib2.urlopen('http://192.168.0.10/read_file.php?filename=default_scan_data%2Fsample_scan_data%2F' + name + '_00_absp.txt&time=0').read()
urllib2.urlopen('http://192.168.0.10/read_file.php?filename=default_scan_data%2Freference_scan_data%2Fref_readings_00.txt&time=0').read()
urllib2.urlopen('http://192.168.0.10/read_file.php?filename=default_scan_data%2Fsample_scan_data%2F' + name + '_00.txt&time=0').read()

Write file when generating patterns :
    var str1=document.getElementById("param_startWavelength").value +"\n"+ document.getElementById("param_endWavelength").value + "\n"+document.getElementById("param_measurementResolution").value + "\n"+document.getElementById("param_totalMeasurementTime").value + "\n"+document.getElementById("param_numScansToAvg").value + "\n"+document.getElementById("param_numPatterns").value +"\n"+start_px + "\n"+end_px+"\n" ;
	
"""