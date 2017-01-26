import pexpect
import math
import string
import random
import math

spectrumPointsNumber  	= 85
numberOfScansToAverage 	= 20
exposureTime			= 1400
pga 					= 1


# run executes the given bash lines on the remote server.
# lines must be an array of strings
# prefer double-quotes (") over simple-quotes (') to avoid escaping issues
def run(lines):
    child = pexpect.spawn('ssh root@192.168.0.10 \'' + ';'.join(lines) + '\'')
    child.expect('.*assword:.*')
    child.sendline('')
    child.expect(pexpect.EOF, timeout = None)
    return child.before[2:-1]
	
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
	"dlp_nirscan -S" + str(spectrumPointsNumber) + " -E600 -fref_readings.txt -L1",
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
		str(pga),
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
	"dlp_nirscan -S" + str(spectrumPointsNumber) + " -E"+ str(exposureTime) +" -fref_readings.txt -L" + str(numberOfScansToAverage),
	"mv avg_readings.txt ref_readings_avg.txt",
	"cd ..",
	"cd ..",
	"rm tmp/*",
	"echo \"Reference set\"",
])

print("pga : " + str(pga))