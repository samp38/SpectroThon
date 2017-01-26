exec 1> log.txt
count=0
cd patterns/
for entry in *
do
case $entry in *.bmp)
count=$((count+1));;
esac
done
dlp_nirscan -l$count
if [ $? -eq 255 ];
 then
 echo "failed" > ../tmp/script_status44.txt
 exit 0
 fi
cd ..
cd custom_scan_data/reference_scan_data/
dlp_nirscan -S85 -E1400 -fref_readings.txt -L2
if [ $? -eq 255 ];
 then
 echo "failed" > ../../tmp/script_status44.txt
 exit 0
 fi
mv avg_readings.txt ref_readings_avg.txt
cd ..
cd ..
rm tmp/*
#Using a more unique string to detect if the script is completed
echo "_?!!SCRIPT_COMPLETED!!?_" > tmp/script_status44.txt