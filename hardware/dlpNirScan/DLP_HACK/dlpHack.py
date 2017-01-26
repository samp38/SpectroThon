import pexpect
import math
import string
import matplotlib.pyplot as plt
import scipy.io as sio
import datetime
import os


# lambdaToPixel converts a wavelength to the units used by the DLP NIRscan.
def lambdaToPixel(wavelength):
	return int(round(-1695.135009765625 + 1.11876213550567626953125 * wavelength + 0.000106355393654666841030120849609375 * wavelength * wavelength))

def pixelToLambda(pixel):
	return int(round(1344.4271240234375 + 0.706179559230804443359375 * pixel -0.0000297453443636186420917510986328125 * (pixel ** 2)))


# run executes the given bash lines on the remote server.
# lines must be an array of strings
# prefer double-quotes (") over simple-quotes (') to avoid escaping issues
def run(lines):
    child = pexpect.spawn('ssh root@192.168.0.10 \'' + ';'.join(lines) + '\'')
    child.expect('.*assword:.*')
    child.sendline('')
    child.expect(pexpect.EOF, timeout = None)
    return child.before[2:-1]
    # return child.before[2:]

def applySettings(_startLambda_, _endLambda_, _startPx_, _endPx_, _spectrumPointsNumber_, _resolution_, _exposureTime_, _measurementTime_, _numberOfScansToAverage_):
	# save the used settings
	print run([
		"cd /usr/share/matrix-gui-2.0",
		"echo \"" + "\n".join([
			str(_startLambda_),
			str(_endLambda_),
			str(_resolution_),
			str(_measurementTime_),
			str(_numberOfScansToAverage_),
			str(_spectrumPointsNumber_),
			str(_startPx_),
			str(_endPx_),
			str(_exposureTime_)
		]) + "\n\" > defaultParameters.txt",
	])
	print run([
		"cd /usr/share/matrix-gui-2.0",
		"echo \"" + "\n".join([
			"Spctrum acquisition date : " + str(datetime.date.today()),
			"*****",
			"start lambda [nm] : " + str(_startLambda_),
			"end lambda [nm] : " + str(_endLambda_),
			"resolution [nm] : " + str(_resolution_),
			"measurement time [ms] : " + str(_measurementTime_),
			"number of scans averaged : " + str(_numberOfScansToAverage_),
			"number of patterns per scan : " + str(_spectrumPointsNumber_),
			"srat pixel : " + str(_startPx_),
			"end pixel : " + str(_endPx_),
			"exposure time [us] : " + str(_exposureTime_)
		]) + "\n\" > defaultParametersCustom.txt",
	])

def generatePatterns(_startPx_, _endPx_, _spectrumPointsNumber_):
	print("Generating Patterns...")
	print run([
		"cd /usr/share/matrix-gui-2.0",
		"rm patterns/*.csv",
		"rm patterns/*.bmp",	
		"rm patterns/*.sdf",		
		"rm tmp/*",		
		"rm *.bmp",		
		"dlp_nirscan -A" + str(_startPx_) + " -Z" + str(_endPx_) + " -N" + str(_spectrumPointsNumber_),
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

# Set reference scan, computes and return pga (gain amplifier)
def setReference(_spectrumPointsNumber_, _exposureTime_, _numberOfScansToAverage_):
	print("Setting Reference...")
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
	
		"for i in {1..20}",
		"    do dlp_nirscan -g1",
		"    if [ $? -eq 0 ]",
		"        then break",
		"    fi",
		"done",
	
		"if [ $i -eq 20 ]",
		"    then echo \"pga_setting_failed\"",
		"    exit 0",
		"fi",
	
		"cd custom_scan_data/reference_scan_data/",
		"dlp_nirscan -S" + str(_spectrumPointsNumber_) + " -E600 -fref_readings.txt -L1",
		"mv avg_readings.txt ref_readings_avg.txt",
		"cd ..",
		"cd ..",
		"rm tmp/*",
	])

	readings = string.split(run([
		"cat /usr/share/matrix-gui-2.0/custom_scan_data/reference_scan_data/ref_readings_00_raw.txt",
	]))
	ref_values = []
	for raw_value in readings:
	    if(int(raw_value[8:],16) & 1 << 1 == 2):
	        ref_values.append(int(raw_value[2:8],16))
	# Compute pga
	ref_max_value = max(ref_values)
	ref_max_value = ref_max_value + 0.2 * ref_max_value
	multiplier = math.floor(8388607/ref_max_value)
	i = 6
	while(i >= 0):
	    if(multiplier >= math.pow(2,i) or i == 0 ):
	        pga = math.pow(2,i)
	        break
	    i = i-1

	# Save PGA settings
	# save the used settings
	print run([
		"cd /usr/share/matrix-gui-2.0/custom_scan_data/reference_scan_data",
		"echo \"" + "\n".join([
			"PGA setting : ",
			str(int(pga)),
		]) + "\n\" > pga_setting.txt",
	])

	# Run reference scan with computed pga
	print run([
		"cd /usr/share/matrix-gui-2.0",	
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
		"cd custom_scan_data/reference_scan_data/",
		"dlp_nirscan -S" + str(_spectrumPointsNumber_) + " -E"+ str(_exposureTime_) +" -fref_readings.txt -L" + str(_numberOfScansToAverage_),
		"mv avg_readings.txt ref_readings_avg.txt",
		"cd ..",
		"cd ..",
		"rm tmp/*",
		"echo \"Reference set\"",
	])

	print("PGA computed : " + str(pga))
	return pga
	
def runScan(_startLambda_, _endLambda_, _spectrumPointsNumber_, _exposureTime_, _numberOfScansToAverage_, _pga_, _reNew_ = False):
	print("Running Scan with pga=" + str(_pga_))
	lambdaValues = []
	columnsPerPattern = math.floor((lambdaToPixel(_endLambda_)-lambdaToPixel(_startLambda_)+1)/_spectrumPointsNumber_)
	extraColumns = (lambdaToPixel(_endLambda_)-lambdaToPixel(_startLambda_)+1)%_spectrumPointsNumber_
	extraColumnsFrequency = math.floor(_spectrumPointsNumber_/extraColumns) if extraColumns > 0 else 0
	currentPatternFirstPixel = lambdaToPixel(_startLambda_)
	for currentPattern in range(0, _spectrumPointsNumber_):
	    nextPatternFirstPixel = currentPatternFirstPixel + columnsPerPattern
	    if extraColumns > 0:
	        if currentPattern % extraColumnsFrequency == 0:
	            nextPatternFirstPixel += 1
	            extraColumns -= 1
	    lambdaValues.append(pixelToLambda((currentPatternFirstPixel + nextPatternFirstPixel - 1) / 2))
	    currentPatternFirstPixel = nextPatternFirstPixel

	if(_reNew_ == False):
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
    		"    do dlp_nirscan -g" + str(_pga_),
    		"    if [ $? -eq 0 ]",
    		"        then break",
    		"    fi",
    		"done",
    		"if [ $i -eq 20 ]",
    		"    then echo \"pga_setting_failed\"",
    		"    exit 0",
    		"fi",
    	])
			
	print run([
   		"cd /usr/share/matrix-gui-2.0/custom_scan_data/sample_scan_data",
		"rm *",
   		"dlp_nirscan -S" + str(_spectrumPointsNumber_) + " -E" + str(_exposureTime_) + " -fpython_custom_scan.txt" + " -L" + str(_numberOfScansToAverage_),
   		"mv avg_readings.txt python_custom_scan_avg.txt",
   		"dlp_nirscan -G -r../reference_scan_data/ref_readings_avg.txt -fpython_custom_scan_avg.txt",
   		"if [ $? -eq 255 ]",
   		"    then echo \"failed\"",
   		"    exit 0",
   		"fi",
   		"cd ..",
   		"cd ..",
   		"rm tmp/*",
   	])
	output                      = {}
	output['lambda']            = lambdaValues
	output['reference_avg']     = [int(value, 16) for value in run(["cat /usr/share/matrix-gui-2.0/custom_scan_data/reference_scan_data/ref_readings_avg.txt"]).split('\n')]
	output['sample_avg']        = [int(value, 16) for value in run(["cat /usr/share/matrix-gui-2.0/custom_scan_data/sample_scan_data/python_custom_scan_avg.txt"]).split('\n')]
	output['sample_avg_absorb'] = [float(value) for value in run(["cat /usr/share/matrix-gui-2.0/custom_scan_data/sample_scan_data/python_custom_scan_avg_absp.txt"]).split('\n')]
	# referenceData    = [int(value, 16) for value in run(["cat /usr/share/matrix-gui-2.0/custom_scan_data/reference_scan_data/ref_readings_avg.txt"]).split('\n')]
	# referenceDataRaw = [int(value, 16) for value in run(["cat /usr/share/matrix-gui-2.0/custom_scan_data/reference_scan_data/ref_readings_00_raw.txt"]).split('\n')]
	# sampleValues     = [int(value, 16) for value in run(["cat /usr/share/matrix-gui-2.0/custom_scan_data/sample_scan_data/python_custom_scan_avg.txt"]).split('\n')]
	# sampleValuesRaw  = [int(value, 16) for value in run(["cat /usr/share/matrix-gui-2.0/custom_scan_data/sample_scan_data/python_custom_scan_00_raw.txt"]).split('\n')]
	# absorbanceValues = [float(value)for value in run(["cat /usr/share/matrix-gui-2.0/custom_scan_data/sample_scan_data/python_custom_scan_avg_absp.txt"]).split('\n')]
	plt.plot(output['lambda'], output['sample_avg_absorb'])
	plt.show()
	return output
	
def getPGA():
    print("Getting pga in DLP_NIRScan filesystem...")
    lines = ["cat /usr/share/matrix-gui-2.0//custom_scan_data/reference_scan_data/pga_setting.txt",]
    child = pexpect.spawn('ssh root@192.168.0.10 \'' + ';'.join(lines) + '\'')
    child.expect('.*assword:.*')
    child.sendline('')
    child.expect(pexpect.EOF, timeout = None)
    pga = child.before[2:].split("\n")[1]
    return pga
	
def saveSpectrum(output):
	today = str(datetime.date.today())
	path = 'data/' + today
	print(today)
	if(os.path.exists(path) == False):
		print('Creating path ' + path)
		os.system('mkdir ' + path)
	name = raw_input("Enter a name for your file\n")
	sio.savemat(path + '/' + name, output)
	params = run([
		"cat /usr/share/matrix-gui-2.0/defaultParametersCustom.txt",
		])
	os.system("echo '" + params + "' > " + path + "/" + name + ".txt")
	print("file saved in " + 'data/' + today)
	